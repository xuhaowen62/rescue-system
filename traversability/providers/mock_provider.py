"""用于验证 Traversability 数据流的模拟 Provider。"""

from typing import Any, Optional

from traversability.interfaces import BaseTraversabilityProvider
from traversability.models import TraversabilityGrid


class MockTraversabilityProvider(BaseTraversabilityProvider):
    """返回固定网格结果的模拟 Provider，不包含可通过性算法。"""

    def __init__(
        self,
        grid: Optional[TraversabilityGrid] = None,
    ) -> None:
        """创建模拟 Provider。"""
        if grid is not None and not isinstance(grid, TraversabilityGrid):
            raise TypeError("grid 必须是 TraversabilityGrid 实例")
        self._grid = grid.copy() if grid is not None else None

    def analyze(self, input_data: Any = None) -> TraversabilityGrid:
        """返回固定的一乘一可通过性网格。"""
        if self._grid is None:
            self._grid = TraversabilityGrid(
                width=1,
                height=1,
                resolution=1.0,
                data=[1.0],
            )
        return self._grid.copy()

    def get_result(self) -> Optional[TraversabilityGrid]:
        """返回最近一次模拟结果。"""
        return self._grid.copy() if self._grid is not None else None

    def reset(self) -> None:
        """清除模拟 Provider 的结果。"""
        self._grid = None