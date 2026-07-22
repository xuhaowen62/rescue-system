"""外部定位算法进程桥接接口。"""

from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional

from localization.models import PoseEstimate, SensorData


class ExternalLocalizationBridge(ABC):
    """定义外部 OpenVINS、LIO-SAM 或 ROS 节点的调用边界。"""

    @abstractmethod
    def initialize(self, parameters: Optional[Mapping[str, Any]] = None) -> None:
        """初始化外部进程或通信通道。"""
        raise NotImplementedError

    @abstractmethod
    def send_sensor_data(self, sensor_data: SensorData) -> None:
        """向外部定位进程发送统一传感器数据。"""
        raise NotImplementedError

    @abstractmethod
    def get_pose(self) -> Optional[PoseEstimate]:
        """读取外部定位进程输出的统一位姿。"""
        raise NotImplementedError

    @abstractmethod
    def shutdown(self) -> None:
        """关闭外部进程或通信通道。"""
        raise NotImplementedError
