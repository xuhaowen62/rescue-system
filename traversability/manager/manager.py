"""Traversability 管理器实现。"""

from typing import Any, Optional

from traversability.exceptions import (
    GridException,
    ProviderException,
    TraversabilityException,
)
from traversability.interfaces import BaseTraversabilityProvider
from traversability.models import TraversabilityGrid


class TraversabilityManager:
    """保存可通过性结果并协调 Provider 数据流。"""

    def __init__(
        self,
        provider: Optional[BaseTraversabilityProvider] = None,
    ) -> None:
        """创建管理器并可选地注入可通过性 Provider。"""
        if provider is not None and not isinstance(
            provider,
            BaseTraversabilityProvider,
        ):
            raise TypeError("provider 必须实现 BaseTraversabilityProvider")
        self._provider = provider
        self._grid: Optional[TraversabilityGrid] = None

    def set_grid(self, grid: TraversabilityGrid) -> TraversabilityGrid:
        """保存可通过性网格并返回保存结果。"""
        if not isinstance(grid, TraversabilityGrid):
            raise GridException("网格类型无效", code="GRID_TYPE_INVALID")
        if not grid.is_valid():
            raise GridException("网格数据无效", code="GRID_DATA_INVALID")
        self._grid = grid.copy()
        return self._grid.copy()

    def get_grid(self) -> Optional[TraversabilityGrid]:
        """返回当前可通过性网格的独立副本。"""
        return self._grid.copy() if self._grid is not None else None

    def update_grid(
        self,
        input_data: Any = None,
    ) -> Optional[TraversabilityGrid]:
        """通过 Provider 获取结果，或直接保存传入网格。"""
        if isinstance(input_data, TraversabilityGrid):
            return self.set_grid(input_data)
        if self._provider is None:
            return self.get_grid()
        try:
            grid = self._provider.analyze(input_data)
            return self.set_grid(grid)
        except (GridException, ProviderException):
            raise
        except Exception as exc:
            raise TraversabilityException(
                "可通过性 Provider 更新失败",
                code="PROVIDER_UPDATE_FAILED",
            ) from exc

    def reset(self) -> None:
        """重置管理器和已注入的 Provider。"""
        if self._provider is not None:
            self._provider.reset()
        self._grid = None