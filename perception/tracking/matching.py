"""ByteTrack 的检测与轨迹匹配工具。"""

import numpy as np
import scipy
from scipy.spatial.distance import cdist

try:
    import lap
except ImportError:
    lap = None
    # TODO：后续补充 lap 缺失时的纯 Python 线性分配实现。

try:
    from cython_bbox import bbox_overlaps as bbox_ious
except ImportError:
    bbox_ious = None
    # TODO：后续补充 cython_bbox 缺失时的纯 Python 交并比实现。

from . import kalman_filter


def merge_matches(m1, m2, shape):
    """合并两组匹配结果，并返回未匹配索引。"""
    o, p, q = shape
    m1 = np.asarray(m1)
    m2 = np.asarray(m2)

    matrix_1 = scipy.sparse.coo_matrix(
        (np.ones(len(m1)), (m1[:, 0], m1[:, 1])),
        shape=(o, p),
    )
    matrix_2 = scipy.sparse.coo_matrix(
        (np.ones(len(m2)), (m2[:, 0], m2[:, 1])),
        shape=(p, q),
    )

    mask = matrix_1 * matrix_2
    match = mask.nonzero()
    match = list(zip(match[0], match[1]))
    unmatched_o = tuple(set(range(o)) - set([i for i, j in match]))
    unmatched_q = tuple(set(range(q)) - set([j for i, j in match]))

    return match, unmatched_o, unmatched_q


def _indices_to_matches(cost_matrix, indices, thresh):
    """根据代价阈值筛选索引匹配结果。"""
    matched_cost = cost_matrix[tuple(zip(*indices))]
    matched_mask = matched_cost <= thresh

    matches = indices[matched_mask]
    unmatched_a = tuple(set(range(cost_matrix.shape[0])) - set(matches[:, 0]))
    unmatched_b = tuple(set(range(cost_matrix.shape[1])) - set(matches[:, 1]))

    return matches, unmatched_a, unmatched_b


def linear_assignment(cost_matrix, thresh):
    """执行带代价阈值的线性分配。"""
    if cost_matrix.size == 0:
        return (
            np.empty((0, 2), dtype=int),
            tuple(range(cost_matrix.shape[0])),
            tuple(range(cost_matrix.shape[1])),
        )
    matches = []
    _cost, x, y = lap.lapjv(
        cost_matrix,
        extend_cost=True,
        cost_limit=thresh,
    )
    for ix, mx in enumerate(x):
        if mx >= 0:
            matches.append([ix, mx])
    unmatched_a = np.where(x < 0)[0]
    unmatched_b = np.where(y < 0)[0]
    matches = np.asarray(matches)
    return matches, unmatched_a, unmatched_b


def ious(atlbrs, btlbrs):
    """计算两组边界框之间的交并比。"""
    iou_matrix = np.zeros(
        (len(atlbrs), len(btlbrs)),
        dtype=np.float64,
    )
    if iou_matrix.size == 0:
        return iou_matrix

    iou_matrix = bbox_ious(
        np.ascontiguousarray(atlbrs, dtype=np.float64),
        np.ascontiguousarray(btlbrs, dtype=np.float64),
    )

    return iou_matrix


def iou_distance(atracks, btracks):
    """根据交并比计算轨迹与检测之间的代价矩阵。"""
    if (
        (len(atracks) > 0 and isinstance(atracks[0], np.ndarray))
        or (len(btracks) > 0 and isinstance(btracks[0], np.ndarray))
    ):
        atlbrs = atracks
        btlbrs = btracks
    else:
        atlbrs = [track.tlbr for track in atracks]
        btlbrs = [track.tlbr for track in btracks]
    _ious = ious(atlbrs, btlbrs)
    cost_matrix = 1 - _ious

    return cost_matrix


def v_iou_distance(atracks, btracks):
    """根据预测边界框的交并比计算代价矩阵。"""
    if (
        (len(atracks) > 0 and isinstance(atracks[0], np.ndarray))
        or (len(btracks) > 0 and isinstance(btracks[0], np.ndarray))
    ):
        atlbrs = atracks
        btlbrs = btracks
    else:
        atlbrs = [track.tlwh_to_tlbr(track.pred_bbox) for track in atracks]
        btlbrs = [track.tlwh_to_tlbr(track.pred_bbox) for track in btracks]
    _ious = ious(atlbrs, btlbrs)
    cost_matrix = 1 - _ious

    return cost_matrix


def embedding_distance(tracks, detections, metric='cosine'):
    """计算轨迹特征与检测特征之间的距离矩阵。"""
    cost_matrix = np.zeros(
        (len(tracks), len(detections)),
        dtype=np.float64,
    )
    if cost_matrix.size == 0:
        return cost_matrix
    det_features = np.asarray(
        [track.curr_feat for track in detections],
        dtype=np.float64,
    )
    track_features = np.asarray(
        [track.smooth_feat for track in tracks],
        dtype=np.float64,
    )
    cost_matrix = np.maximum(
        0.0,
        cdist(track_features, det_features, metric),
    )
    return cost_matrix


def gate_cost_matrix(
    kf, cost_matrix, tracks, detections, only_position=False
):
    """根据卡尔曼滤波门控距离过滤匹配代价。"""
    if cost_matrix.size == 0:
        return cost_matrix
    gating_dim = 2 if only_position else 4
    gating_threshold = kalman_filter.chi2inv95[gating_dim]
    measurements = np.asarray([det.to_xyah() for det in detections])
    for row, track in enumerate(tracks):
        gating_distance = kf.gating_distance(
            track.mean,
            track.covariance,
            measurements,
            only_position,
        )
        cost_matrix[row, gating_distance > gating_threshold] = np.inf
    return cost_matrix


def fuse_motion(
    kf, cost_matrix, tracks, detections,
    only_position=False, lambda_=0.98
):
    """将卡尔曼滤波运动距离融合到匹配代价中。"""
    if cost_matrix.size == 0:
        return cost_matrix
    gating_dim = 2 if only_position else 4
    gating_threshold = kalman_filter.chi2inv95[gating_dim]
    measurements = np.asarray([det.to_xyah() for det in detections])
    for row, track in enumerate(tracks):
        gating_distance = kf.gating_distance(
            track.mean,
            track.covariance,
            measurements,
            only_position,
            metric='maha',
        )
        cost_matrix[row, gating_distance > gating_threshold] = np.inf
        cost_matrix[row] = (
            lambda_ * cost_matrix[row]
            + (1 - lambda_) * gating_distance
        )
    return cost_matrix


def fuse_iou(cost_matrix, tracks, detections):
    """融合特征相似度与交并比相似度。"""
    if cost_matrix.size == 0:
        return cost_matrix
    reid_sim = 1 - cost_matrix
    iou_dist = iou_distance(tracks, detections)
    iou_sim = 1 - iou_dist
    fuse_sim = reid_sim * (1 + iou_sim) / 2
    fuse_cost = 1 - fuse_sim
    return fuse_cost


def fuse_score(cost_matrix, detections):
    """将检测置信度融合到交并比代价中。"""
    if cost_matrix.size == 0:
        return cost_matrix
    iou_sim = 1 - cost_matrix
    det_scores = np.array([det.score for det in detections])
    det_scores = np.expand_dims(det_scores, axis=0).repeat(
        cost_matrix.shape[0],
        axis=0,
    )
    fuse_sim = iou_sim * det_scores
    fuse_cost = 1 - fuse_sim
    return fuse_cost
