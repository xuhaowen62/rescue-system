"""Traversability 到 Planning 的抽象适配接口。"""

from abc import ABC, abstractmethod
from typing import Optional

from planning.models import CostMap


class BasePlanningAdapter(ABC):
    """定义向 Planning 传递 CostMap 的统一协议。"""

    @abstractmethod
    def send_costmap(self, costmap: CostMap) -> None:
        """向 Planning 发送代价地图。"""
        raise NotImplementedError

    @abstractmethod
    def update(self) -> Optional[CostMap]:
        """更新并返回最近一次发送的代价地图。"""
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        """重置 Planning 适配器状态。"""
        raise NotImplementedError