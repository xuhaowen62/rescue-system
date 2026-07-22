"""定位模块扩展接口。"""

from localization.adapters.base_adapter import BaseLocalizationAdapter
from localization.adapters.lidar import LioSAMAdapter
from localization.adapters.camera_adapter import CameraLocalizationAdapter
from localization.adapters.imu_adapter import IMULocalizationAdapter
from localization.adapters.lidar_adapter import (
    LiDARLocalizationAdapter,
    LidarLocalizationAdapter,
)
from localization.adapters.mock_adapter import MockLocalizationAdapter
from localization.adapters.vio import OpenVINSAdapter

__all__ = [
    "BaseLocalizationAdapter",
    "CameraLocalizationAdapter",
    "IMULocalizationAdapter",
    "LioSAMAdapter",
    "LiDARLocalizationAdapter",
    "LidarLocalizationAdapter",
    "MockLocalizationAdapter",
    "OpenVINSAdapter",
]
