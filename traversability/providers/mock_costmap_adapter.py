"""用于验证 Traversability 到 CostMap 数据流的模拟适配器。"""

from typing import Optional

from planning.models import CostMap
from traversability.exceptions import GridException
from traversability.interfaces import BaseCostMapAdapter
from traversability.models import TraversabilityGrid


class MockCostMapAdapter(BaseCostMapAdapter):
    """使用固定线性映射生成 CostMap，不包含复杂代价算法。"""

    def __init__(self) -> None:
        """创建模拟代价地图适配器。"""
        self._costmap: Optional[CostMap] = None

    def convert_to_costmap(
        self,
        grid: TraversabilityGrid,
    ) -> CostMap:
        """将可通过性值按一减可通过性的方式映射到零到一百。"""
        if not self.validate_input(grid):
            raise GridException(
                "输入可通过性网格无效",
                code="GRID_INPUT_INVALID",
            )
        data = [(1.0 - value) * 100.0 for value in grid.data]
        self._costmap = CostMap(
            width=grid.width,
            height=grid.height,
            resolution=grid.resolution,
            data=data,
            timestamp=grid.timestamp,
            frame_id=grid.frame_id,
            metadata={"source": "traversability"},
        )
        return self._costmap.copy()

    def validate_input(self, grid: TraversabilityGrid) -> bool:
        """检查输入是否为有效的可通过性网格。"""
        return isinstance(grid, TraversabilityGrid) and grid.is_valid()

    def reset(self) -> None:
        """清除最近一次生成的代价地图。"""
        self._costmap = None