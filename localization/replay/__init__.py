"""定位数据回放接口。"""

from localization.replay.interface import ReplayInterface
from localization.replay.mock_replay import MockReplay

__all__ = ["MockReplay", "ReplayInterface"]
