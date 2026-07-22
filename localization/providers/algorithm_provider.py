"""定位模块扩展接口。"""

from abc import ABC, abstractmethod
from typing import Optional

from localization.adapters import BaseLocalizationAdapter
from localization.models import PoseEstimate, SensorData


class BaseLocalizationAlgorithmProvider(ABC):
    """定义本模块的统一接口或数据结构。"""

    @abstractmethod
    def set_adapter(self, adapter: BaseLocalizationAdapter) -> None:
        """执行本模块定义的标准处理步骤。"""
        raise NotImplementedError

    @abstractmethod
    def initialize(self) -> None:
        """执行本模块定义的标准处理步骤。"""
        raise NotImplementedError

    @abstractmethod
    def process_sensor_data(self, sensor_data: SensorData) -> PoseEstimate:
        """执行本模块定义的标准处理步骤。"""
        raise NotImplementedError

    @abstractmethod
    def get_pose(self) -> Optional[PoseEstimate]:
        """执行本模块定义的标准处理步骤。"""
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        """执行本模块定义的标准处理步骤。"""
        raise NotImplementedError


BaseAlgorithmProvider = BaseLocalizationAlgorithmProvider
