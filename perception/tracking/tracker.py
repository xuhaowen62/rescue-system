"""提供与 ByteTrack 解耦的统一跟踪入口。"""

from typing import TYPE_CHECKING, Dict, List, Set

import cv2
import numpy as np

from .bytetrack import BYTETracker as _BYTETracker
from .bytetrack import STrack as _STrack

if TYPE_CHECKING:
    from ultralytics.engine.results import Results


class Tracker:
    """封装 ByteTrack 的统一目标跟踪接口。"""

    def __init__(self) -> None:
        """初始化内部 ByteTrack 实例和轨迹缓存。"""
        self._tracker = _BYTETracker()
        self._tracks: List[_STrack] = []
        self._track_ids_seen: Set[int] = set()

    def update(self, results: "Results") -> List[_STrack]:
        """接收检测结果，更新跟踪状态并返回当前轨迹。

        参数:
            results: Ultralytics 返回的单帧 Results 对象。

        返回:
            当前帧中已经激活的轨迹列表。
        """
        self._tracks = list(self._tracker.update(results))
        self._remember_track_ids()
        return self.get_tracks()

    def get_tracks(self) -> List[_STrack]:
        """返回当前缓存的轨迹列表。"""
        return list(self._tracks)

    def reset(self) -> None:
        """清空轨迹缓存并重新初始化内部 ByteTrack 实例。"""
        self._tracker = _BYTETracker()
        self._tracks.clear()
        self._track_ids_seen.clear()

    def draw(self, frame: np.ndarray) -> np.ndarray:
        """在图像上绘制当前目标框、Track ID 和置信度。

        参数:
            frame: 待绘制的图像数组。

        返回:
            绘制后的图像数组。
        """
        output = frame.copy()
        for track in self._tracks:
            self._draw_track(output, track)
        # TODO：后续增加轨迹线和速度信息。
        return output

    def statistics(self) -> Dict[str, int]:
        """返回当前跟踪状态统计信息。

        返回字典包含以下字段：
            current_count: 当前缓存的目标数量。
            total_created: 累计产生的轨迹数量。
            lost_count: 当前已丢失轨迹数量。
            removed_count: 当前已移除轨迹数量。
        """
        return {
            "current_count": len(self._tracks),
            "total_created": len(self._track_ids_seen),
            "lost_count": len(self._tracker.lost_stracks),
            "removed_count": len(self._tracker.removed_stracks),
        }

    def _remember_track_ids(self) -> None:
        """记录内部 ByteTrack 已经产生过的轨迹编号。"""
        track_groups = (
            self._tracker.tracked_stracks,
            self._tracker.lost_stracks,
            self._tracker.removed_stracks,
        )
        for tracks in track_groups:
            self._track_ids_seen.update(track.track_id for track in tracks)

    @staticmethod
    def _draw_track(frame: np.ndarray, track: _STrack) -> None:
        """在图像上绘制单条轨迹的边界框和文字信息。"""
        x1, y1, x2, y2 = (int(value) for value in track.tlbr)
        color = (0, 255, 0)
        label = f"ID: {track.track_id} Conf: {track.score:.2f}"
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            frame,
            label,
            (x1, max(0, y1 - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2,
            cv2.LINE_AA,
        )
