"""位姿提供器抽象接口。"""

from abc import ABC, abstractmethod
from typing import Optional

from localization.models import PoseState, SensorData


class BasePoseProvider(ABC):
    """定义定位数据源必须提供的统一接口。"""

    @abstractmethod
    def get_pose(self) -> Optional[PoseState]:
        """读取当前位姿。"""
        raise NotImplementedError

    @abstractmethod
    def update(self) -> Optional[PoseState]:
        """获取一次最新位姿。"""
        raise NotImplementedError

    @abstractmethod
    def process_sensor_data(self, sensor_data: SensorData) -> PoseState:
        """接收传感器数据并返回定位位姿。"""
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        """重置位姿数据源。"""
        raise NotImplementedError