"""Traversability 到 Planning CostMap 的抽象适配接口。"""

from abc import ABC, abstractmethod

from planning.models import CostMap
from traversability.models import TraversabilityGrid


class BaseCostMapAdapter(ABC):
    """定义可通过性网格转换为 Planning CostMap 的统一协议。"""

    @abstractmethod
    def convert_to_costmap(
        self,
        grid: TraversabilityGrid,
    ) -> CostMap:
        """将可通过性网格转换为规划代价地图。"""
        raise NotImplementedError

    @abstractmethod
    def validate_input(self, grid: TraversabilityGrid) -> bool:
        """检查输入可通过性网格是否满足转换要求。"""
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        """重置适配器状态。"""
        raise NotImplementedError