"""基于 Ultralytics Results 的 ByteTrack 多目标跟踪实现。"""

from typing import TYPE_CHECKING, Any, List, Tuple

import numpy as np

from . import matching
from .basetrack import BaseTrack, TrackState
from .kalman_filter import KalmanFilter

if TYPE_CHECKING:
    from ultralytics.engine.results import Results


class STrack(BaseTrack):
    """表示单个目标的 ByteTrack 轨迹。"""

    shared_kalman = KalmanFilter()

    def __init__(self, tlwh: np.ndarray, score: float) -> None:
        """使用左上角坐标、宽度、高度和置信度创建轨迹。"""
        self._tlwh = np.asarray(tlwh, dtype=np.float64)
        self.kalman_filter = None
        self.mean = None
        self.covariance = None
        self.is_activated = False

        self.score = score
        self.tracklet_len = 0

    def predict(self) -> None:
        """使用卡尔曼滤波器预测轨迹位置。"""
        mean_state = self.mean.copy()
        if self.state != TrackState.Tracked:
            mean_state[7] = 0
        self.mean, self.covariance = self.kalman_filter.predict(
            mean_state,
            self.covariance,
        )

    @staticmethod
    def multi_predict(stracks: List["STrack"]) -> None:
        """批量预测多个轨迹的位置。"""
        if len(stracks) > 0:
            multi_mean = np.asarray([st.mean.copy() for st in stracks])
            multi_covariance = np.asarray([st.covariance for st in stracks])
            for i, st in enumerate(stracks):
                if st.state != TrackState.Tracked:
                    multi_mean[i][7] = 0
            multi_mean, multi_covariance = STrack.shared_kalman.multi_predict(
                multi_mean,
                multi_covariance,
            )
            for i, (mean, cov) in enumerate(
                zip(multi_mean, multi_covariance)
            ):
                stracks[i].mean = mean
                stracks[i].covariance = cov

    def activate(self, kalman_filter: KalmanFilter, frame_id: int) -> None:
        """使用当前观测激活一条新轨迹。"""
        self.kalman_filter = kalman_filter
        self.track_id = self.next_id()
        self.mean, self.covariance = self.kalman_filter.initiate(
            self.tlwh_to_xyah(self._tlwh)
        )

        self.tracklet_len = 0
        self.state = TrackState.Tracked
        if frame_id == 1:
            self.is_activated = True
        self.frame_id = frame_id
        self.start_frame = frame_id

    def re_activate(
        self,
        new_track: "STrack",
        frame_id: int,
        new_id: bool = False,
    ) -> None:
        """使用新的观测重新激活丢失轨迹。"""
        self.mean, self.covariance = self.kalman_filter.update(
            self.mean,
            self.covariance,
            self.tlwh_to_xyah(new_track.tlwh),
        )
        self.tracklet_len = 0
        self.state = TrackState.Tracked
        self.is_activated = True
        self.frame_id = frame_id
        if new_id:
            self.track_id = self.next_id()
        self.score = new_track.score

    def update(self, new_track: "STrack", frame_id: int) -> None:
        """使用匹配到的新观测更新当前轨迹。"""
        self.frame_id = frame_id
        self.tracklet_len += 1

        new_tlwh = new_track.tlwh
        self.mean, self.covariance = self.kalman_filter.update(
            self.mean,
            self.covariance,
            self.tlwh_to_xyah(new_tlwh),
        )
        self.state = TrackState.Tracked
        self.is_activated = True

        self.score = new_track.score

    @property
    def tlwh(self) -> np.ndarray:
        """返回左上角坐标、宽度和高度格式的当前边界框。"""
        if self.mean is None:
            return self._tlwh.copy()
        ret = self.mean[:4].copy()
        ret[2] *= ret[3]
        ret[:2] -= ret[2:] / 2
        return ret

    @property
    def tlbr(self) -> np.ndarray:
        """返回左上角和右下角坐标格式的当前边界框。"""
        ret = self.tlwh.copy()
        ret[2:] += ret[:2]
        return ret

    @staticmethod
    def tlwh_to_xyah(tlwh: np.ndarray) -> np.ndarray:
        """将边界框转换为中心点、宽高比和高度格式。"""
        ret = np.asarray(tlwh).copy()
        ret[:2] += ret[2:] / 2
        ret[2] /= ret[3]
        return ret

    def to_xyah(self) -> np.ndarray:
        """返回当前轨迹的中心点、宽高比和高度表示。"""
        return self.tlwh_to_xyah(self.tlwh)

    @staticmethod
    def tlbr_to_tlwh(tlbr: np.ndarray) -> np.ndarray:
        """将左上角和右下角坐标转换为左上角、宽度和高度格式。"""
        ret = np.asarray(tlbr).copy()
        ret[2:] -= ret[:2]
        return ret

    @staticmethod
    def tlwh_to_tlbr(tlwh: np.ndarray) -> np.ndarray:
        """将左上角、宽度和高度转换为左上角和右下角坐标格式。"""
        ret = np.asarray(tlwh).copy()
        ret[2:] += ret[:2]
        return ret

    def __repr__(self) -> str:
        """返回轨迹的调试表示。"""
        return "OT_{}_({}-{})".format(
            self.track_id,
            self.start_frame,
            self.end_frame,
        )


class BYTETracker(object):
    """实现 ByteTrack 核心多目标跟踪流程。"""

    def __init__(
        self,
        track_thresh: float = 0.5,
        track_buffer: int = 30,
        match_thresh: float = 0.8,
        frame_rate: int = 30,
        mot20: bool = False,
    ) -> None:
        """初始化跟踪阈值、轨迹缓存和卡尔曼滤波器。

        参数:
            track_thresh: 高置信度检测阈值。
            track_buffer: 轨迹最大丢失帧数基准。
            match_thresh: 第一阶段关联的代价阈值。
            frame_rate: 输入视频帧率。
            mot20: 是否使用 MOT20 模式；关闭时融合检测置信度。
        """
        self.tracked_stracks: List[STrack] = []
        self.lost_stracks: List[STrack] = []
        self.removed_stracks: List[STrack] = []

        self.frame_id = 0
        self.track_thresh = track_thresh
        self.match_thresh = match_thresh
        self.mot20 = mot20
        self.det_thresh = track_thresh + 0.1
        self.buffer_size = int(frame_rate / 30.0 * track_buffer)
        self.max_time_lost = self.buffer_size
        self.kalman_filter = KalmanFilter()

    def update(self, results: "Results") -> List[STrack]:
        """接收单个 Ultralytics Results 并更新跟踪状态。

        参数:
            results: Ultralytics 返回的单个 ``Results`` 对象。

        返回:
            当前帧中已经激活的轨迹列表。
        """
        self.frame_id += 1
        activated_stracks: List[STrack] = []
        refind_stracks: List[STrack] = []
        lost_stracks: List[STrack] = []
        removed_stracks: List[STrack] = []

        bboxes, scores = self._extract_detections(results)
        remain_inds = scores > self.track_thresh
        inds_low = scores > 0.1
        inds_high = scores < self.track_thresh

        inds_second = np.logical_and(inds_low, inds_high)
        dets_second = bboxes[inds_second]
        dets = bboxes[remain_inds]
        scores_keep = scores[remain_inds]
        scores_second = scores[inds_second]

        if len(dets) > 0:
            detections = [
                STrack(STrack.tlbr_to_tlwh(tlbr), score)
                for tlbr, score in zip(dets, scores_keep)
            ]
        else:
            detections = []

        unconfirmed: List[STrack] = []
        tracked_stracks: List[STrack] = []
        for track in self.tracked_stracks:
            if not track.is_activated:
                unconfirmed.append(track)
            else:
                tracked_stracks.append(track)

        strack_pool = joint_stracks(tracked_stracks, self.lost_stracks)
        STrack.multi_predict(strack_pool)
        dists = matching.iou_distance(strack_pool, detections)
        if not self.mot20:
            dists = matching.fuse_score(dists, detections)
        matches, u_track, u_detection = matching.linear_assignment(
            dists,
            thresh=self.match_thresh,
        )

        for itracked, idet in matches:
            track = strack_pool[itracked]
            det = detections[idet]
            if track.state == TrackState.Tracked:
                track.update(det, self.frame_id)
                activated_stracks.append(track)
            else:
                track.re_activate(det, self.frame_id, new_id=False)
                refind_stracks.append(track)

        if len(dets_second) > 0:
            detections_second = [
                STrack(STrack.tlbr_to_tlwh(tlbr), score)
                for tlbr, score in zip(dets_second, scores_second)
            ]
        else:
            detections_second = []
        r_tracked_stracks = [
            strack_pool[i]
            for i in u_track
            if strack_pool[i].state == TrackState.Tracked
        ]
        dists = matching.iou_distance(
            r_tracked_stracks,
            detections_second,
        )
        matches, u_track, _u_detection_second = matching.linear_assignment(
            dists,
            thresh=0.5,
        )
        for itracked, idet in matches:
            track = r_tracked_stracks[itracked]
            det = detections_second[idet]
            if track.state == TrackState.Tracked:
                track.update(det, self.frame_id)
                activated_stracks.append(track)
            else:
                track.re_activate(det, self.frame_id, new_id=False)
                refind_stracks.append(track)

        for it in u_track:
            track = r_tracked_stracks[it]
            if track.state != TrackState.Lost:
                track.mark_lost()
                lost_stracks.append(track)

        detections = [detections[i] for i in u_detection]
        dists = matching.iou_distance(unconfirmed, detections)
        if not self.mot20:
            dists = matching.fuse_score(dists, detections)
        matches, u_unconfirmed, u_detection = matching.linear_assignment(
            dists,
            thresh=0.7,
        )
        for itracked, idet in matches:
            unconfirmed[itracked].update(detections[idet], self.frame_id)
            activated_stracks.append(unconfirmed[itracked])
        for it in u_unconfirmed:
            track = unconfirmed[it]
            track.mark_removed()
            removed_stracks.append(track)

        for inew in u_detection:
            track = detections[inew]
            if track.score < self.det_thresh:
                continue
            track.activate(self.kalman_filter, self.frame_id)
            activated_stracks.append(track)

        for track in self.lost_stracks:
            if self.frame_id - track.end_frame > self.max_time_lost:
                track.mark_removed()
                removed_stracks.append(track)

        self.tracked_stracks = [
            track
            for track in self.tracked_stracks
            if track.state == TrackState.Tracked
        ]
        self.tracked_stracks = joint_stracks(
            self.tracked_stracks,
            activated_stracks,
        )
        self.tracked_stracks = joint_stracks(
            self.tracked_stracks,
            refind_stracks,
        )
        self.lost_stracks = sub_stracks(
            self.lost_stracks,
            self.tracked_stracks,
        )
        self.lost_stracks.extend(lost_stracks)
        self.lost_stracks = sub_stracks(
            self.lost_stracks,
            self.removed_stracks,
        )
        self.removed_stracks.extend(removed_stracks)
        self.tracked_stracks, self.lost_stracks = remove_duplicate_stracks(
            self.tracked_stracks,
            self.lost_stracks,
        )

        return [
            track
            for track in self.tracked_stracks
            if track.is_activated
        ]

    @staticmethod
    def _to_numpy(value: Any) -> np.ndarray:
        """将 Ultralytics 张量或数组转换为 NumPy 数组。"""
        if hasattr(value, "detach"):
            value = value.detach()
        if hasattr(value, "cpu"):
            value = value.cpu()
        return np.asarray(value)

    @classmethod
    def _extract_detections(
        cls,
        results: "Results",
    ) -> Tuple[np.ndarray, np.ndarray]:
        """从 Ultralytics Results 提取边界框和置信度。"""
        boxes = results.boxes
        bboxes = cls._to_numpy(boxes.xyxy).reshape(-1, 4)
        scores = cls._to_numpy(boxes.conf).reshape(-1)
        return bboxes, scores


ByteTrack = BYTETracker


def joint_stracks(
    tlista: List[STrack],
    tlistb: List[STrack],
) -> List[STrack]:
    """合并两组轨迹并按照轨迹编号去重。"""
    exists = {}
    res = []
    for track in tlista:
        exists[track.track_id] = 1
        res.append(track)
    for track in tlistb:
        tid = track.track_id
        if not exists.get(tid, 0):
            exists[tid] = 1
            res.append(track)
    return res


def sub_stracks(
    tlista: List[STrack],
    tlistb: List[STrack],
) -> List[STrack]:
    """从第一组轨迹中移除第二组轨迹。"""
    stracks = {}
    for track in tlista:
        stracks[track.track_id] = track
    for track in tlistb:
        tid = track.track_id
        if stracks.get(tid, 0):
            del stracks[tid]
    return list(stracks.values())


def remove_duplicate_stracks(
    stracksa: List[STrack],
    stracksb: List[STrack],
) -> Tuple[List[STrack], List[STrack]]:
    """移除两组轨迹中重复的边界框。"""
    pdist = matching.iou_distance(stracksa, stracksb)
    pairs = np.where(pdist < 0.15)
    dupa, dupb = list(), list()
    for p, q in zip(*pairs):
        timep = stracksa[p].frame_id - stracksa[p].start_frame
        timeq = stracksb[q].frame_id - stracksb[q].start_frame
        if timep > timeq:
            dupb.append(q)
        else:
            dupa.append(p)
    resa = [
        track
        for i, track in enumerate(stracksa)
        if i not in dupa
    ]
    resb = [
        track
        for i, track in enumerate(stracksb)
        if i not in dupb
    ]
    return resa, resb
