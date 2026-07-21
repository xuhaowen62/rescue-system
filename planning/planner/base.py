"""Planner 抽象基类。"""

from abc import ABC, abstractmethod
from typing import Optional

from planning.core import PlanningResult
from planning.models import Goal, OccupancyGrid, Path, Pose, Velocity


class BaseGlobalPlanner(ABC):
    """全局规划器统一接口，不包含具体规划算法。"""

    def __init__(self) -> None:
        """初始化全局规划器的通用运行状态。"""
        self._status = PlanningResult.RUNNING
        self._current_path: Optional[Path] = None

    @abstractmethod
    def plan(
        self,
        start: Pose,
        goal: Goal,
        occupancy_grid: OccupancyGrid,
    ) -> Path:
        """根据起点、目标和地图生成路径。"""
        raise NotImplementedError

    def validate_goal(self, goal: Goal) -> bool:
        """验证目标是否为 Planning 统一目标模型。"""
        return isinstance(goal, Goal) and isinstance(goal.pose, Pose)

    def validate_pose(self, pose: Pose) -> bool:
        """验证位姿是否为 Planning 统一位姿模型。"""
        return isinstance(pose, Pose)

    def validate_map(self, occupancy_grid: OccupancyGrid) -> bool:
        """验证地图是否为 Planning 统一占据栅格模型。"""
        return isinstance(occupancy_grid, OccupancyGrid)

    def reset(self) -> None:
        """清除规划器当前路径并恢复初始状态。"""
        self._status = PlanningResult.RUNNING
        self._current_path = None

    def cancel(self) -> None:
        """取消当前规划任务并清除当前路径。"""
        self._status = PlanningResult.FAILURE
        self._current_path = None

    def get_status(self) -> PlanningResult:
        """返回规划器最近一次操作状态。"""
        return self._status

    def get_current_path(self) -> Optional[Path]:
        """返回规划器最近一次生成的路径。"""
        return self._current_path

    def _set_path(self, path: Path) -> Path:
        """保存规划结果并标记操作成功。"""
        self._current_path = path
        self._status = PlanningResult.SUCCESS
        return path

    def _set_failure(self) -> None:
        """标记最近一次规划操作失败。"""
        self._status = PlanningResult.FAILURE
        self._current_path = None


class BaseLocalPlanner(ABC):
    """局部规划器统一接口，不包含具体控制算法。"""

    def __init__(self) -> None:
        """初始化局部规划器的通用运行状态。"""
        self._status = PlanningResult.RUNNING
        self._path: Optional[Path] = None
        self._paused = False
        self._last_velocity = Velocity()

    @abstractmethod
    def compute_velocity(
        self,
        current_pose: Pose,
        path: Optional[Path] = None,
        current_velocity: Optional[Velocity] = None,
    ) -> Velocity:
        """根据当前位姿和路径生成速度。"""
        raise NotImplementedError

    def set_path(self, path: Path) -> None:
        """设置局部规划器当前跟随路径。"""
        self._path = path
        self._paused = False
        self._status = PlanningResult.RUNNING

    def clear_path(self) -> None:
        """清除局部规划器当前跟随路径。"""
        self._path = None
        self._last_velocity = Velocity()
        self._status = PlanningResult.RUNNING

    def pause(self) -> None:
        """暂停局部规划器输出。"""
        self._paused = True
        self._last_velocity = Velocity()
        self._status = PlanningResult.RUNNING

    def resume(self) -> None:
        """恢复局部规划器运行。"""
        self._paused = False
        self._status = PlanningResult.RUNNING

    def stop(self) -> None:
        """停止局部规划器并清零速度。"""
        self._last_velocity = Velocity()
        self._status = PlanningResult.RUNNING

    def reset(self) -> None:
        """重置局部规划器状态。"""
        self._status = PlanningResult.RUNNING
        self._path = None
        self._paused = False
        self._last_velocity = Velocity()

    def get_status(self) -> PlanningResult:
        """返回局部规划器最近一次操作状态。"""
        return self._status
