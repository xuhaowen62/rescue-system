"""Localization 到 Planning 的位姿适配接口。"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from planning.models import Pose as PlanningPose

from localization.models import PoseEstimate, PoseState

if TYPE_CHECKING:
    from localization.manager import LocalizationManager


class BasePlanningAdapter(ABC):
    """定义 Planning 读取 Localization 位姿的最小协议。"""

    @abstractmethod
    def get_pose(self) -> Optional[PoseState]:
        """向 Planning 提供当前位姿。"""
        raise NotImplementedError


class LocalizationPlanningAdapter(BasePlanningAdapter):
    """将 LocalizationManager 的 PoseEstimate 转换为 Planning Pose。"""

    def __init__(self, manager: "LocalizationManager") -> None:
        """创建绑定到指定定位管理器的 Planning 适配器。"""
        from localization.manager import LocalizationManager

        if not isinstance(manager, LocalizationManager):
            raise TypeError("manager must be LocalizationManager")
        self._manager = manager

    def get_pose(self) -> Optional[PlanningPose]:
        """返回 Planning 模块使用的位姿模型。"""
        estimate = self._manager.get_current_pose()
        if estimate is None:
            return None
        return PlanningPose(
            x=estimate.pose.x,
            y=estimate.pose.y,
            z=estimate.pose.z,
            roll=estimate.pose.roll,
            pitch=estimate.pose.pitch,
            yaw=estimate.pose.yaw,
            frame_id=estimate.frame_id,
            timestamp=estimate.timestamp,
        )

    def get_pose_estimate(self) -> Optional[PoseEstimate]:
        """返回未转换的统一 PoseEstimate，便于联调和诊断。"""
        return self._manager.get_current_pose()

    def get_localization_state(self) -> str:
        """返回定位状态。"""
        return self._manager.get_localization_state()
