"""救援任务数据模型。"""

from dataclasses import dataclass, field
from datetime import datetime

from ..config import MissionConfig
from .search_state import SearchState


@dataclass
class RescueTask:
    """描述一个待执行或执行中的救援任务。

    Attributes:
        task_id: 救援任务的业务唯一标识。
        survivor_id: 任务关联的幸存者标识。
        priority: 任务优先级。
        status: 任务当前状态。
        assigned_robot: 被分配执行任务的机器人标识。
        create_time: 任务创建时间。
        finish_time: 任务完成时间。
        description: 任务补充描述。
    """

    task_id: str
    survivor_id: str
    priority: int = MissionConfig.DEFAULT_PRIORITY
    status: SearchState = SearchState.SEARCHING
    assigned_robot: str | None = None
    create_time: datetime = field(default_factory=datetime.now)
    finish_time: datetime | None = None
    description: str = ""
