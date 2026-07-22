"""可通过性多模态处理模块。"""

from abc import ABC, abstractmethod
from typing import Sequence

from traversability.models import FeatureRepresentation


class BaseFeatureFusion(ABC):
    """定义本模块的统一接口或数据结构。"""

    @abstractmethod
    def fuse(
        self,
        features: Sequence[FeatureRepresentation],
    ) -> FeatureRepresentation:
        """定义本模块的统一接口或数据结构。"""
        raise NotImplementedError
