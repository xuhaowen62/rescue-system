"""可通过性多模态处理模块。"""

from abc import ABC, abstractmethod

from traversability.models import FeatureRepresentation, SensorData


class BaseEncoder(ABC):
    """定义本模块的统一接口或数据结构。"""

    @abstractmethod
    def encode(self, sensor_data: SensorData) -> FeatureRepresentation:
        """执行本模块定义的标准处理步骤。"""
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        """执行本模块定义的标准处理步骤。"""
        raise NotImplementedError
