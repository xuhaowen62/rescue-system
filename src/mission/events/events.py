"""Mission 事件类型和事件数据模型。"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class MissionEventType(Enum):
    """定义 Mission 业务层可识别的事件类型。"""

    SURVIVOR_DETECTED = "survivor_detected"
    SURVIVOR_CONFIRMED = "survivor_confirmed"
    SURVIVOR_RESCUED = "survivor_rescued"
    RESCUE_TASK_CREATED = "rescue_task_created"
    RESCUE_TASK_FINISHED = "rescue_task_finished"
    SEARCH_STATE_CHANGED = "search_state_changed"


@dataclass
class MissionEvent:
    """描述一个 Mission 业务事件。

    Attributes:
        event_type: 事件类型。
        timestamp: 事件发生时间。
        survivor_id: 关联的幸存者标识。
        task_id: 关联的救援任务标识。
        payload: 事件的附加数据。
    """

    event_type: MissionEventType
    timestamp: datetime = field(default_factory=datetime.now)
    survivor_id: str | None = None
    task_id: str | None = None
    payload: dict[str, object] = field(default_factory=dict)
