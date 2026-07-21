"""Traversability Provider 抽象接口。"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from traversability.models import TraversabilityGrid


class BaseTraversabilityProvider(ABC):
    """定义可通过性数据源必须提供的统一接口。"""

    @abstractmethod
    def analyze(self, input_data: Any = None) -> TraversabilityGrid:
        """接收输入数据并返回可通过性网格结果。"""
        raise NotImplementedError

    @abstractmethod
    def get_result(self) -> Optional[TraversabilityGrid]:
        """读取最近一次可通过性分析结果。"""
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        """重置可通过性数据源。"""
        raise NotImplementedError