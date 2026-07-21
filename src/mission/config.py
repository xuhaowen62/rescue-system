"""Mission 业务层的统一配置。"""

from typing import ClassVar


class MissionConfig:
    """集中保存 Mission 业务层使用的配置参数。"""

    MAX_SURVIVOR_MEMORY: ClassVar[int] = 1000
    CONFIRM_THRESHOLD: ClassVar[float] = 0.8
    MAX_LOST_TIME: ClassVar[float] = 5.0
    SAVE_INTERVAL: ClassVar[float] = 1.0
    DEFAULT_PRIORITY: ClassVar[int] = 0
