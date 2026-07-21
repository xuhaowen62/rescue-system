"""传感器数据提供器抽象接口。"""

from abc import ABC, abstractmethod
from typing import Optional

from localization.models import SensorData


class BaseSensorProvider(ABC):
    """定义传感器数据源必须提供的统一接口。"""

    @abstractmethod
    def get_sensor_data(self) -> Optional[SensorData]:
        """读取当前传感器数据。"""
        raise NotImplementedError

    @abstractmethod
    def update(self) -> Optional[SensorData]:
        """获取一次最新传感器数据。"""
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        """重置传感器数据源。"""
        raise NotImplementedError