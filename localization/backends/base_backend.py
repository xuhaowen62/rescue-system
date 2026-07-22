"""定位模块的统一接口和数据流处理。"""

from abc import ABC, abstractmethod
from typing import Optional

from localization.models import PoseEstimate, SensorData


class BaseLocalizationBackend(ABC):
    """定位模块的统一接口和数据流处理。"""

    @abstractmethod
    def initialize(self) -> None:
        """定位模块的统一接口和数据流处理。"""
        raise NotImplementedError

    @abstractmethod
    def process(
        self,
        sensor_data: SensorData,
        adapter_pose: Optional[PoseEstimate] = None,
    ) -> PoseEstimate:
        """定位模块的统一接口和数据流处理。"""
        raise NotImplementedError

    @abstractmethod
    def get_pose(self) -> Optional[PoseEstimate]:
        """定位模块的统一接口和数据流处理。"""
        raise NotImplementedError

    @abstractmethod
    def shutdown(self) -> None:
        """定位模块的统一接口和数据流处理。"""
        raise NotImplementedError
