"""Localization 到 Traversability 的位姿适配接口。"""

from typing import Dict, Optional, Tuple, TYPE_CHECKING

from localization.models import PoseEstimate
from localization.utils.transform import Transform

if TYPE_CHECKING:
    from localization.manager import LocalizationManager


class LocalizationTraversabilityAdapter:
    """向 Traversability 提供机器人位置、坐标变换和时间信息。"""

    def __init__(self, manager: "LocalizationManager") -> None:
        """创建绑定到指定定位管理器的 Traversability 适配器。"""
        from localization.manager import LocalizationManager

        if not isinstance(manager, LocalizationManager):
            raise TypeError("manager must be LocalizationManager")
        self._manager = manager

    def get_pose(self) -> Optional[PoseEstimate]:
        """返回当前统一位姿。"""
        return self._manager.get_current_pose()

    def get_robot_position(self) -> Optional[Tuple[float, float, float]]:
        """返回当前机器人位置 ``(x, y, z)``。"""
        pose = self.get_pose()
        return pose.position if pose is not None else None

    def get_transform(self) -> Optional[Transform]:
        """返回当前机器人位姿对应的坐标变换。"""
        return self._manager.get_transform()

    def get_time_sync_info(self) -> Optional[Dict[str, object]]:
        """返回供可通过性数据对齐使用的轻量时间信息。"""
        pose = self.get_pose()
        if pose is None:
            return None
        return {
            "timestamp": pose.timestamp,
            "frame_id": pose.frame_id,
            "source": pose.source,
        }

    def get_localization_state(self) -> str:
        """返回当前定位状态。"""
        return self._manager.get_localization_state()
