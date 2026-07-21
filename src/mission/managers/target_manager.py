"""搜救目标管理器。"""

from typing import TYPE_CHECKING, Dict, List

from ..models.survivor import Survivor
from ..utils.converter import tracks_to_survivors

if TYPE_CHECKING:
    from perception.tracking.bytetrack import STrack


class TargetManager:
    """维护当前有效的 Survivor 集合。"""

    def __init__(self) -> None:
        """初始化目标管理器。"""
        self._survivors: Dict[int, Survivor] = {}

    def update_tracks(self, tracks: List["STrack"]) -> List[Survivor]:
        """接收 Tracking 轨迹并更新当前 Survivor 集合。

        Args:
            tracks: Tracking 模块输出的轨迹列表。

        Returns:
            更新后的当前 Survivor 列表。
        """
        current_survivors = tracks_to_survivors(tracks)
        current_ids = {
            survivor.track_id
            for survivor in current_survivors
            if survivor.track_id is not None
        }

        for survivor in current_survivors:
            if survivor.track_id is None:
                continue
            existing = self._survivors.get(survivor.track_id)
            if existing is None:
                self._survivors[survivor.track_id] = survivor
            else:
                self._merge_survivor(existing, survivor)

        stale_ids = set(self._survivors) - current_ids
        for track_id in stale_ids:
            del self._survivors[track_id]
        return self.get_all_survivors()

    def get_survivor(self, track_id: int) -> Survivor | None:
        """根据 Tracking 的轨迹编号获取 Survivor。

        Args:
            track_id: Tracking 分配的轨迹编号。

        Returns:
            对应的 Survivor，不存在时返回 None。
        """
        return self._survivors.get(track_id)

    def get_all_survivors(self) -> List[Survivor]:
        """返回当前所有有效 Survivor。"""
        return list(self._survivors.values())

    def count(self) -> int:
        """返回当前有效 Survivor 数量。"""
        return len(self._survivors)

    def exists(self, track_id: int) -> bool:
        """检查指定轨迹编号是否存在。

        Args:
            track_id: Tracking 分配的轨迹编号。

        Returns:
            存在时返回 True，否则返回 False。
        """
        return track_id in self._survivors

    def remove(self, track_id: int) -> bool:
        """移除指定轨迹编号对应的 Survivor。

        Args:
            track_id: Tracking 分配的轨迹编号。

        Returns:
            成功移除时返回 True，否则返回 False。
        """
        return self._survivors.pop(track_id, None) is not None

    def reset(self) -> None:
        """重置目标管理器并清空当前 Survivor。"""
        self._survivors.clear()

    def clear(self) -> None:
        """清空当前 Survivor。"""
        self._survivors.clear()

    @staticmethod
    def _merge_survivor(
        existing: Survivor,
        current: Survivor,
    ) -> None:
        """将新的观测字段合并到已有 Survivor。"""
        existing.track_id = current.track_id
        existing.status = current.status
        existing.confidence = current.confidence
        existing.bbox = current.bbox
        existing.image_position = current.image_position
        existing.last_seen = current.last_seen
        existing.frame_count = current.frame_count
        if existing.first_seen is None:
            existing.first_seen = current.first_seen
