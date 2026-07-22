"""定位数据 Mock 回放实现。"""

from copy import deepcopy
from typing import Any, List, Optional

from localization.replay.interface import ReplayInterface


class MockReplay(ReplayInterface):
    """使用内存列表回放统一定位数据。"""

    def __init__(self, data: Optional[List[Any]] = None) -> None:
        """创建 Mock 回放器。"""
        self._data = [deepcopy(item) for item in (data or [])]
        self._index = 0

    def add_data(self, data: Any) -> None:
        """加入一条数据的独立副本。"""
        self._data.append(deepcopy(data))

    def read_next(self) -> Optional[Any]:
        """读取下一条数据的独立副本。"""
        if not self.has_next():
            return None
        value = deepcopy(self._data[self._index])
        self._index += 1
        return value

    def has_next(self) -> bool:
        """判断回放游标是否未到末尾。"""
        return self._index < len(self._data)

    def reset(self) -> None:
        """将回放游标重置到开头。"""
        self._index = 0
