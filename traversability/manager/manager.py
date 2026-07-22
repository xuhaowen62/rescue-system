"""Traversability 管理器实现。"""

from typing import Any, Optional

from planning.models import CostMap
from traversability.exceptions import (
    GridException,
    ProviderException,
    TraversabilityException,
)
from traversability.interfaces import (
    BaseCostMapAdapter,
    BaseTraversabilityProvider,
)
from traversability.models import TraversabilityGrid


class TraversabilityManager:
    """保存可通过性结果并协调网格与 CostMap 数据流。"""

    def __init__(
        self,
        provider: Optional[BaseTraversabilityProvider] = None,
        costmap_adapter: Optional[BaseCostMapAdapter] = None,
    ) -> None:
        """创建管理器并注入可选 Provider 和 CostMap 适配器。"""
        if provider is not None and not isinstance(
            provider,
            BaseTraversabilityProvider,
        ):
            raise TypeError("provider 必须实现 BaseTraversabilityProvider")
        if costmap_adapter is not None and not isinstance(
            costmap_adapter,
            BaseCostMapAdapter,
        ):
            raise TypeError("costmap_adapter 必须实现 BaseCostMapAdapter")
        self._provider = provider
        self._costmap_adapter = costmap_adapter
        self._grid: Optional[TraversabilityGrid] = None
        self._costmap: Optional[CostMap] = None

    def set_grid(self, grid: TraversabilityGrid) -> TraversabilityGrid:
        """保存可通过性网格并清除过期 CostMap。"""
        if not isinstance(grid, TraversabilityGrid):
            raise GridException("网格类型无效", code="GRID_TYPE_INVALID")
        if not grid.is_valid():
            raise GridException("网格数据无效", code="GRID_DATA_INVALID")
        self._grid = grid.copy()
        self._costmap = None
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

    def get_costmap(self) -> Optional[CostMap]:
        """返回当前 Planning CostMap 的独立副本。"""
        return self._costmap.copy() if self._costmap is not None else None

    def update_costmap(
        self,
        grid: Optional[TraversabilityGrid] = None,
    ) -> Optional[CostMap]:
        """通过适配器将可通过性网格转换为 Planning CostMap。"""
        if grid is not None:
            self.set_grid(grid)
        if self._grid is None:
            return None
        if self._costmap_adapter is None:
            raise ProviderException(
                "未设置 CostMap 适配器",
                code="COSTMAP_ADAPTER_NOT_SET",
            )
        try:
            costmap = self._costmap_adapter.convert_to_costmap(self._grid)
            if not isinstance(costmap, CostMap):
                raise ProviderException(
                    "适配器返回类型无效",
                    code="COSTMAP_TYPE_INVALID",
                )
            self._costmap = costmap.copy()
            return self._costmap.copy()
        except (GridException, ProviderException):
            raise
        except Exception as exc:
            raise TraversabilityException(
                "CostMap 转换失败",
                code="COSTMAP_CONVERSION_FAILED",
            ) from exc

    def reset(self) -> None:
        """重置管理器、Provider 和 CostMap 适配器。"""
        if self._provider is not None:
            self._provider.reset()
        if self._costmap_adapter is not None:
            self._costmap_adapter.reset()
        self._grid = None
        self._costmap = None