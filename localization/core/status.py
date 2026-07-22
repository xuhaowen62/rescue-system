"""定位模块的状态定义。"""

from enum import Enum


class LocalizationStatus(str, Enum):
    """描述定位管理器及其后端的生命周期状态。"""

    IDLE = "IDLE"
    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    READY = "READY"
    LOST = "LOST"
    FAILED = "FAILED"
    UPDATING = "UPDATING"
    NO_POSE = "NO_POSE"
    NO_SENSOR_DATA = "NO_SENSOR_DATA"
