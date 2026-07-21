"""Planning 管理器。"""

from typing import Optional

from planning.config import PlannerConfig
from planning.core import PlanningResult, PlanningState
from planning.exceptions import GoalException, PlanningException
from planning.factory import PlannerFactory
from planning.controller.base import BaseController
from planning.models import (
    CostMap,
    Goal,
    OccupancyGrid,
    Path,
    PlanningStatus,
    Pose,
    RobotState,
    Velocity,
)
from planning.planner.base import BaseGlobalPlanner, BaseLocalPlanner


class PlanningManager:
    """组织 Goal、Path、Velocity 和 RobotState 的数据流。"""

    def __init__(
        self,
        global_planner: Optional[BaseGlobalPlanner] = None,
        local_planner: Optional[BaseLocalPlanner] = None,
        controller: Optional[BaseController] = None,
        planner_factory: Optional[PlannerFactory] = None,
        planner_config: Optional[PlannerConfig] = None,
    ) -> None:
        """创建规划管理器并注入可插拔的规划组件。"""
        self._global_planner = global_planner
        self._local_planner = local_planner
        self._controller = controller
        self._planner_factory = planner_factory
        self._planner_config = planner_config
        self._state = PlanningState.IDLE
        self._result = PlanningResult.RUNNING
        self._map: Optional[OccupancyGrid] = None
        self._costmap: Optional[CostMap] = None
        self._goal: Optional[Goal] = None
        self._path: Optional[Path] = None
        self._velocity = Velocity()
        self._robot_state: Optional[RobotState] = None
        self._message = ""
        self._error_code: Optional[str] = None

    @property
    def state(self) -> PlanningState:
        """返回当前规划状态。"""
        return self._state

    def set_goal(self, goal: Goal) -> PlanningStatus:
        """设置当前目标并等待规划请求。"""
        if not isinstance(goal, Goal):
            raise GoalException(
                "规划目标类型无效",
                code="GOAL_TYPE_INVALID",
            )
        self._goal = goal
        self.clear_path()
        self._velocity = Velocity()
        self._result = PlanningResult.RUNNING
        self._message = "已接收规划目标，等待规划"
        self._error_code = None
        self._state = PlanningState.WAITING_GOAL
        return self.get_status()

    def get_goal(self) -> Optional[Goal]:
        """返回当前目标。"""
        return self._goal

    def clear_goal(self) -> None:
        """清除当前目标并停止当前数据流。"""
        self._stop_controller()
        self._goal = None
        self.clear_path()
        self._velocity = Velocity()
        self._result = PlanningResult.RUNNING
        self._message = "已清除规划目标"
        self._error_code = None
        self._state = PlanningState.IDLE

    def set_map(self, occupancy_grid: OccupancyGrid) -> None:
        """设置规划使用的占据栅格地图。"""
        if not isinstance(occupancy_grid, OccupancyGrid):
            raise PlanningException(
                "占据栅格地图类型无效",
                code="MAP_TYPE_INVALID",
            )
        self._map = occupancy_grid
        self.clear_path()
        self._message = "已设置占据栅格地图"

    def get_map(self) -> Optional[OccupancyGrid]:
        """返回当前占据栅格地图。"""
        return self._map

    def set_costmap(self, costmap: CostMap) -> None:
        """??????????????"""
        if not isinstance(costmap, CostMap):
            raise PlanningException(
                "????????",
                code="COSTMAP_TYPE_INVALID",
            )
        self._costmap = costmap
        self.clear_path()
        self._message = "???????"

    def get_costmap(self) -> Optional[CostMap]:
        """?????????"""
        return self._costmap

    def request_plan(
        self,
        start: Pose,
        goal: Optional[Goal] = None,
    ) -> Optional[Path]:
        """调用全局规划器生成路径，不包含具体规划算法。"""
        if not isinstance(start, Pose):
            raise PlanningException(
                "规划起点类型无效",
                code="POSE_TYPE_INVALID",
            )
        if goal is not None:
            self.set_goal(goal)
        if self._goal is None:
            self._fail(
                PlanningState.WAITING_GOAL,
                "未设置规划目标",
                "GOAL_NOT_SET",
            )
            return None
        if not self._ensure_components():
            return None
        if self._map is None:
            self._fail(
                PlanningState.BLOCKED,
                "未设置占据栅格地图",
                "MAP_NOT_SET",
            )
            return None
        if self._global_planner is None:
            self._state = PlanningState.PLANNING
            self._result = PlanningResult.RUNNING
            self._message = "等待全局规划器"
            self._error_code = "PLANNER_NOT_SET"
            return None

        self._state = PlanningState.PLANNING
        self._result = PlanningResult.RUNNING
        try:
            path = self._global_planner.plan(start, self._goal, self._map)
        except PlanningException as exc:
            self._path = None
            self._set_exception(exc, PlanningState.FAILED)
            return None
        except Exception as exc:
            self._path = None
            self._fail(
                PlanningState.FAILED,
                f"全局规划器调用失败: {exc}",
                "PLANNER_ERROR",
            )
            return None

        if path is None:
            self._path = None
            self._fail(
                PlanningState.BLOCKED,
                "全局规划器未返回路径",
                "PATH_NOT_FOUND",
            )
            return None
        if not isinstance(path, Path):
            self._path = None
            self._fail(
                PlanningState.FAILED,
                "全局规划器返回了无效路径类型",
                "PATH_TYPE_INVALID",
            )
            return None
        if not path.is_valid():
            self._path = path
            self._fail(
                PlanningState.BLOCKED,
                "全局规划器返回了无效路径",
                "PATH_INVALID",
            )
            return None

        self._path = path
        try:
            if self._local_planner is not None:
                self._local_planner.set_path(path)
        except PlanningException as exc:
            self._set_exception(exc, PlanningState.FAILED)
            return None
        except Exception as exc:
            self._fail(
                PlanningState.FAILED,
                f"局部规划器设置路径失败: {exc}",
                "LOCAL_PLANNER_ERROR",
            )
            return None
        self._robot_state = RobotState(
            pose=start,
            velocity=self._velocity,
            timestamp=start.timestamp,
        )
        self._state = PlanningState.FOLLOWING
        self._result = PlanningResult.SUCCESS
        self._message = "已生成规划路径"
        self._error_code = None
        return path

    def get_current_path(self) -> Optional[Path]:
        """返回当前路径。"""
        return self._path

    def clear_path(self) -> None:
        """清除当前路径并回到等待状态。"""
        if self._local_planner is not None:
            self._local_planner.clear_path()
        self._path = None
        if self._goal is None:
            self._state = PlanningState.IDLE
        else:
            self._state = PlanningState.WAITING_GOAL

    def follow_path(
        self,
        current_pose: Optional[Pose] = None,
        current_velocity: Optional[Velocity] = None,
    ) -> PlanningStatus:
        """调用局部规划器或控制器生成并发送速度。"""
        if not self._ensure_components():
            return self.get_status()
        if self._path is None:
            self._fail(
                PlanningState.BLOCKED,
                "当前没有可跟随路径",
                "PATH_NOT_SET",
            )
            return self.get_status()
        if self._controller is None:
            self._state = PlanningState.FOLLOWING
            self._result = PlanningResult.RUNNING
            self._message = "等待控制器"
            self._error_code = "CONTROLLER_NOT_SET"
            return self.get_status()

        pose = current_pose
        if pose is None and self._robot_state is not None:
            pose = self._robot_state.pose
        if pose is None:
            pose = Pose()
        if not isinstance(pose, Pose):
            raise PlanningException(
                "当前位姿类型无效",
                code="POSE_TYPE_INVALID",
            )
        velocity = current_velocity or self._velocity
        if not isinstance(velocity, Velocity):
            raise PlanningException(
                "当前速度类型无效",
                code="VELOCITY_TYPE_INVALID",
            )

        self._state = PlanningState.FOLLOWING
        self._result = PlanningResult.RUNNING
        try:
            self._controller.start()
            if self._local_planner is not None:
                command = self._local_planner.compute_velocity(
                    pose,
                    self._path,
                    velocity,
                )
            else:
                command = self._controller.compute_velocity(
                    pose,
                    self._path,
                    velocity,
                )
            if not isinstance(command, Velocity) or not command.is_valid():
                raise PlanningException(
                    "速度组件返回了无效速度",
                    code="VELOCITY_INVALID",
                )
            self._controller.send_velocity(command)
        except PlanningException as exc:
            self._stop_controller()
            self._set_exception(exc, PlanningState.FAILED)
            return self.get_status()
        except Exception as exc:
            self._stop_controller()
            self._fail(
                PlanningState.FAILED,
                f"控制器调用失败: {exc}",
                "CONTROLLER_ERROR",
            )
            return self.get_status()

        self._velocity = command
        self._robot_state = RobotState(
            pose=pose,
            velocity=command,
            timestamp=pose.timestamp,
        )
        self._state = PlanningState.FOLLOWING
        self._result = PlanningResult.SUCCESS
        self._message = "已生成并发送速度指令"
        self._error_code = None
        return self.get_status()

    def get_status(self) -> PlanningStatus:
        """返回当前规划状态快照。"""
        return PlanningStatus(
            state=self._state,
            result=self._result,
            goal=self._goal,
            path=self._path,
            velocity=self._velocity,
            robot_state=self._robot_state,
            message=self._message,
            error_code=self._error_code,
        )

    def reset(self) -> None:
        """重置管理器及已注入组件的运行状态。"""
        self._stop_controller()
        if self._global_planner is not None:
            self._global_planner.reset()
        if self._local_planner is not None:
            self._local_planner.reset()
        if self._controller is not None:
            self._controller.reset()
        self._state = PlanningState.IDLE
        self._result = PlanningResult.RUNNING
        self._map = None
        self._costmap = None
        self._goal = None
        self._path = None
        self._velocity = Velocity()
        self._robot_state = None
        self._message = ""
        self._error_code = None

    def cancel(self) -> PlanningStatus:
        """取消当前规划任务并停止控制器。"""
        self.clear_goal()
        self._message = "规划任务已取消"
        return self.get_status()

    def update(
        self,
        current_pose: Optional[Pose] = None,
        current_velocity: Optional[Velocity] = None,
    ) -> PlanningStatus:
        """执行一次兼容性的管理器更新。"""
        if self._path is None and current_pose is not None:
            self.request_plan(current_pose)
        if self._path is None:
            return self.get_status()
        return self.follow_path(current_pose, current_velocity)

    def request_replanning(self, reason: str = "") -> PlanningStatus:
        """标记需要重新规划，等待下一次规划请求。"""
        if self._goal is None:
            self._fail(
                PlanningState.WAITING_GOAL,
                "无活动目标，无法重新规划",
                "GOAL_NOT_SET",
            )
            return self.get_status()
        self._state = PlanningState.REPLANNING
        self._result = PlanningResult.RUNNING
        self._message = reason or "已请求重新规划"
        self._error_code = None
        return self.get_status()

    def mark_arrived(self) -> PlanningStatus:
        """由外部模块显式标记已到达目标。"""
        self._stop_controller()
        self._state = PlanningState.ARRIVED
        self._result = PlanningResult.SUCCESS
        self._velocity = Velocity()
        self._message = "已到达目标"
        self._error_code = None
        return self.get_status()

    def _ensure_components(self) -> bool:
        """根据配置通过工厂惰性创建尚未注入的组件。"""
        if self._planner_factory is None or self._planner_config is None:
            return True
        try:
            if (
                self._global_planner is None
                and self._planner_config.planner_name
            ):
                self._global_planner = (
                    self._planner_factory.create_global_planner(
                        self._planner_config.planner_name,
                        self._planner_config.planner_parameters,
                    )
                )
            if (
                self._local_planner is None
                and self._planner_config.local_planner_name
            ):
                self._local_planner = (
                    self._planner_factory.create_local_planner(
                        self._planner_config.local_planner_name,
                        self._planner_config.planner_parameters,
                    )
                )
            if (
                self._controller is None
                and self._planner_config.controller_name
            ):
                self._controller = self._planner_factory.create_controller(
                    self._planner_config.controller_name,
                    self._planner_config.controller_parameters,
                )
        except PlanningException as exc:
            self._set_exception(exc, PlanningState.FAILED)
            return False
        return True

    def _fail(
        self,
        state: PlanningState,
        message: str,
        error_code: str,
    ) -> None:
        """记录失败状态。"""
        self._state = state
        self._result = PlanningResult.FAILURE
        self._message = message
        self._error_code = error_code

    def _set_exception(
        self,
        exception: PlanningException,
        state: PlanningState,
    ) -> None:
        """将 Planning 异常转换为统一状态快照。"""
        self._fail(state, exception.message, exception.code)

    def _stop_controller(self) -> None:
        """安全停止控制器输出。"""
        if self._controller is not None:
            self._controller.stop()
