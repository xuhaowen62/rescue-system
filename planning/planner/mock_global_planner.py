"""全局规划器 Mock 实现。"""

from planning.models import Goal, OccupancyGrid, Path, Pose, Waypoint
from planning.planner.base import BaseGlobalPlanner


class MockGlobalPlanner(BaseGlobalPlanner):
    """用于验证规划数据流的最小全局规划器。"""

    def plan(
        self,
        start: Pose,
        goal: Goal,
        occupancy_grid: OccupancyGrid,
    ) -> Path:
        """返回由起点和目标点组成的 Mock 路径，不执行路径规划。"""
        if not (
            self.validate_pose(start)
            and self.validate_goal(goal)
            and self.validate_map(occupancy_grid)
        ):
            self._set_failure()
            return Path(is_valid=False)
        return self._set_path(
            Path(
                waypoints=(Waypoint(pose=start), Waypoint(pose=goal.pose)),
                is_valid=True,
            )
        )
