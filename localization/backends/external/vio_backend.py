"""定位模块的统一接口和数据流处理。"""

from typing import Any, Optional

from localization.backends.external.base_external_backend import (
    ExternalLocalizationBackend,
)
from localization.models import PoseEstimate, SensorData


class VIOBackend(ExternalLocalizationBackend):
    """定位模块的统一接口和数据流处理。"""

    def __init__(self, **parameters: Any) -> None:
        """定位模块的统一接口和数据流处理。"""
        self._parameters = dict(parameters)
        self._initialized = False
        self._pose: Optional[PoseEstimate] = None

    def initialize(self) -> None:
        """定位模块的统一接口和数据流处理。"""
        self._initialized = True

    def process_image(self, sensor_data: SensorData) -> Optional[PoseEstimate]:
        """定位模块的统一接口和数据流处理。"""
        self._ensure_initialized()
        self._validate_sensor_data(sensor_data)
        return self.get_pose()

    def process_imu(self, sensor_data: SensorData) -> Optional[PoseEstimate]:
        """定位模块的统一接口和数据流处理。"""
        self._ensure_initialized()
        self._validate_sensor_data(sensor_data)
        return self.get_pose()

    def get_pose(self) -> Optional[PoseEstimate]:
        """定位模块的统一接口和数据流处理。"""
        return self._pose.copy() if self._pose is not None else None

    def shutdown(self) -> None:
        """定位模块的统一接口和数据流处理。"""
        self._initialized = False
        self._pose = None

    def _ensure_initialized(self) -> None:
        """定位模块的统一接口和数据流处理。"""
        if not self._initialized:
            raise RuntimeError("backend is not initialized")

    @staticmethod
    def _validate_sensor_data(sensor_data: SensorData) -> None:
        """定位模块的统一接口和数据流处理。"""
        if not isinstance(sensor_data, SensorData):
            raise TypeError("sensor_data must be SensorData")
        if not sensor_data.is_valid():
            raise ValueError("sensor_data is invalid")
