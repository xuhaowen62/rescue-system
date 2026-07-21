"""控制器 Mock 实现。"""

from typing import Optional

from planning.controller.base import BaseController
from planning.core import PlanningResult
from planning.models import Path, Pose, Velocity


class MockController(BaseController):
    """用于验证控制数据流的最小控制器。"""

    def __init__(self) -> None:
        """创建默认输出零速度的 Mock 控制器。"""
        super().__init__()

    @property
    def last_velocity(self) -> Velocity:
        """返回最近一次发送的速度。"""
        return self._last_velocity

    def compute_velocity(
        self,
        current_pose: Pose,
        path: Path,
        current_velocity: Optional[Velocity] = None,
    ) -> Velocity:
        """返回默认速度，不执行任何控制算法。"""
        del current_pose, path, current_velocity
        self._last_velocity = Velocity()
        self._status = PlanningResult.SUCCESS
        return self._last_velocity

    def send_velocity(self, velocity: Velocity) -> None:
        """保存最近一次速度指令。"""
        self._last_velocity = velocity
        self._status = PlanningResult.SUCCESS

    def stop(self) -> None:
        """停止控制器并将最近速度置为零。"""
        self._started = False
        self._paused = False
        self._last_velocity = Velocity()
        self._status = PlanningResult.RUNNING


