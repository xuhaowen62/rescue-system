"""地图数据源抽象接口。"""

from abc import ABC, abstractmethod
from typing import Optional

from planning.models.map import OccupancyGrid


class BaseMapProvider(ABC):
    """地图提供器统一抽象接口，不包含地图生成或处理算法。"""

    @abstractmethod
    def get_map(self) -> Optional[OccupancyGrid]:
        """获取当前可用的占据栅格地图。"""
        raise NotImplementedError

    @abstractmethod
    def update_map(self, occupancy_grid: OccupancyGrid) -> None:
        """接收外部模块提供的占据栅格地图。"""
        raise NotImplementedError

    @abstractmethod
    def clear_map(self) -> None:
        """清除当前地图引用。"""
        raise NotImplementedError