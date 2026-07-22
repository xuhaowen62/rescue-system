"""Traversability Provider 抽象接口。"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from traversability.core import TraversabilityStatus
from traversability.models import TraversabilityGrid


class BaseTraversabilityProvider(ABC):
    """定义可通过性数据源必须提供的统一接口。"""

    @abstractmethod
    def analyze(self, input_data: Any = None) -> TraversabilityGrid:
        """接收输入数据并返回可通过性网格。"""
        raise NotImplementedError

    @abstractmethod
    def get_result(self) -> Optional[TraversabilityGrid]:
        """读取最近一次分析结果。"""
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        """重置可通过性数据源。"""
        raise NotImplementedError

    def get_status(self) -> TraversabilityStatus:
        """返回 Provider 当前状态。"""
        return getattr(self, "_status", TraversabilityStatus.IDLE)

    def _set_status(self, status: TraversabilityStatus) -> None:
        """设置 Provider 当前状态。"""
        self._status = status
