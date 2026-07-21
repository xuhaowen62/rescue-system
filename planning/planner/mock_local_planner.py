"""局部规划器 Mock 实现。"""

from typing import Optional

from planning.core import PlanningResult
from planning.models import Path, Pose, Velocity
from planning.planner.base import BaseLocalPlanner


class MockLocalPlanner(BaseLocalPlanner):
    """用于验证局部规划数据流的最小局部规划器。"""

    def compute_velocity(
        self,
        current_pose: Pose,
        path: Optional[Path] = None,
        current_velocity: Optional[Velocity] = None,
    ) -> Velocity:
        """返回默认速度，不执行任何控制算法。"""
        del current_pose, current_velocity
        active_path = path or self._path
        if active_path is None or self._paused:
            self._set_failure()
            return Velocity()
        self._last_velocity = Velocity()
        self._status = PlanningResult.SUCCESS
        return self._last_velocity

    def _set_failure(self) -> None:
        """标记 Mock 局部规划操作失败。"""
        self._status = PlanningResult.FAILURE
        self._last_velocity = Velocity()


