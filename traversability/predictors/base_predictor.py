"""可通过性多模态处理模块。"""

from abc import ABC, abstractmethod

from traversability.models import FeatureRepresentation, TraversabilityGrid


class BasePredictor(ABC):
    """定义本模块的统一接口或数据结构。"""

    @abstractmethod
    def predict(self, feature: FeatureRepresentation) -> TraversabilityGrid:
        """执行本模块定义的标准处理步骤。"""
        raise NotImplementedError
