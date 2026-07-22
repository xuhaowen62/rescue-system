"""定位模块的统一接口和数据流处理。"""

from typing import Optional

from localization.backends.base_backend import BaseLocalizationBackend
from localization.exceptions import LocalizationException, PoseException
from localization.models import PoseEstimate, PoseState, SensorData


class MockLocalizationBackend(BaseLocalizationBackend):
    """定位模块的统一接口和数据流处理。"""

    def __init__(self, source: str = "mock-backend") -> None:
        """定位模块的统一接口和数据流处理。"""
        self._source = str(source).strip() or "mock-backend"
        self._estimate: Optional[PoseEstimate] = None
        self._initialized = False

    def initialize(self) -> None:
        """定位模块的统一接口和数据流处理。"""
        self._initialized = True

    def process(
        self,
        sensor_data: SensorData,
        adapter_pose: Optional[PoseEstimate] = None,
    ) -> PoseEstimate:
        """定位模块的统一接口和数据流处理。"""
        if not self._initialized:
            raise LocalizationException(
                "backend is not initialized",
                code="BACKEND_NOT_INITIALIZED",
            )
        if not isinstance(sensor_data, SensorData):
            raise TypeError("sensor_data must be SensorData")
        if not sensor_data.is_valid():
            raise PoseException(
                "sensor data is invalid",
                code="SENSOR_DATA_INVALID",
            )
        if adapter_pose is not None:
            if not isinstance(adapter_pose, PoseEstimate):
                raise TypeError("adapter_pose must be PoseEstimate")
            if not adapter_pose.is_valid():
                raise PoseException(
                    "adapter pose is invalid",
                    code="ADAPTER_POSE_INVALID",
                )
            pose = adapter_pose.pose.copy()
            frame_id = adapter_pose.frame_id
            covariance = adapter_pose.covariance
        else:
            pose = PoseState(frame_id=sensor_data.frame_id)
            frame_id = sensor_data.frame_id
            covariance = None
        timestamp = sensor_data.timestamp
        if timestamp is None:
            timestamp = 0.0
        pose.timestamp = timestamp
        pose.frame_id = frame_id or "map"
        self._estimate = PoseEstimate(
            timestamp=timestamp,
            frame_id=pose.frame_id,
            pose=pose,
            covariance=covariance,
            source=self._source,
        )
        return self._estimate.copy()

    def get_pose(self) -> Optional[PoseEstimate]:
        """定位模块的统一接口和数据流处理。"""
        return self._estimate.copy() if self._estimate is not None else None

    def shutdown(self) -> None:
        """定位模块的统一接口和数据流处理。"""
        self._initialized = False
        self._estimate = None
