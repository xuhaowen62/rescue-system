"""Planning 状态快照数据模型。"""

from dataclasses import dataclass, field
from typing import Optional

from planning.core.state import PlanningResult, PlanningState
from planning.models.goal import Goal
from planning.models.path import Path
from planning.models.robot_state import RobotState
from planning.models.velocity import Velocity


@dataclass(frozen=True)
class PlanningStatus:
    """表示规划管理器对外提供的只读状态快照。"""

    state: PlanningState = PlanningState.IDLE
    result: PlanningResult = PlanningResult.RUNNING
    goal: Optional[Goal] = None
    path: Optional[Path] = None
    velocity: Velocity = field(default_factory=Velocity)
    robot_state: Optional[RobotState] = None
    message: str = ""
    error_code: Optional[str] = None
