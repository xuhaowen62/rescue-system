"""Controller 抽象基类。"""

from abc import ABC, abstractmethod
from typing import Optional

from planning.core import PlanningResult
from planning.models import Path, Pose, Velocity


class BaseController(ABC):
    """控制器统一接口，不包含具体控制算法。"""

    def __init__(self) -> None:
        """初始化控制器的通用运行状态。"""
        self._status = PlanningResult.RUNNING
        self._started = False
        self._paused = False
        self._last_velocity = Velocity()

    def start(self) -> None:
        """启动控制器输出。"""
        self._started = True
        self._paused = False
        self._status = PlanningResult.RUNNING

    @abstractmethod
    def stop(self) -> None:
        """停止控制器并清零速度。"""
        raise NotImplementedError

    def pause(self) -> None:
        """暂停控制器输出。"""
        self._paused = True
        self._last_velocity = Velocity()
        self._status = PlanningResult.RUNNING

    def resume(self) -> None:
        """恢复控制器输出。"""
        self._paused = False
        self._started = True
        self._status = PlanningResult.RUNNING

    def reset(self) -> None:
        """重置控制器状态。"""
        self._started = False
        self._paused = False
        self._last_velocity = Velocity()
        self._status = PlanningResult.RUNNING

    def get_status(self) -> PlanningResult:
        """返回控制器最近一次操作状态。"""
        return self._status

    @abstractmethod
    def compute_velocity(
        self,
        current_pose: Pose,
        path: Path,
        current_velocity: Optional[Velocity] = None,
    ) -> Velocity:
        """根据当前位姿和路径生成速度指令。"""
        raise NotImplementedError

    @abstractmethod
    def send_velocity(self, velocity: Velocity) -> None:
        """发送速度指令。"""
        raise NotImplementedError
