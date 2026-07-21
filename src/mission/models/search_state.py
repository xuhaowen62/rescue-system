"""Mission 搜索状态定义。"""

from enum import Enum


class SearchState(Enum):
    """表示搜救目标或任务所处的搜索状态。"""

    SEARCHING = "searching"
    TRACKING = "tracking"
    CONFIRMED = "confirmed"
    REPORTING = "reporting"
    RESCUING = "rescuing"
    FINISHED = "finished"
