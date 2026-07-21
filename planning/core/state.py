"""Planning 状态定义。"""

from enum import Enum, auto


class PlanningState(Enum):
    """描述规划管理器当前所处的生命周期状态。"""

    IDLE = auto()
    WAITING_GOAL = auto()
    PLANNING = auto()
    FOLLOWING = auto()
    BLOCKED = auto()
    REPLANNING = auto()
    PAUSED = auto()
    ARRIVED = auto()
    FAILED = auto()


class PlanningResult(Enum):
    """描述最近一次规划或跟随操作的结果。"""

    SUCCESS = auto()
    FAILURE = auto()
    RUNNING = auto()
