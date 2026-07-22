"""定位模块接口。"""

from typing import Any, Optional

from localization.backends.external.lidar_slam_backend import LidarSLAMBackend
from localization.exceptions import PoseException
from localization.models import PoseEstimate, PoseState, SensorData


class LioSAMBackend(LidarSLAMBackend):
    """定位模块接口。"""

    def __init__(self, **parameters: Any) -> None:
        """定位模块接口。"""
        super().__init__(**parameters)
        self._source = str(parameters.get("source", "liosam")).strip() or "liosam"
        self._output_frame_id = (
            str(parameters.get("output_frame_id", "map")).strip() or "map"
        )
        self._last_pointcloud_input: Optional[SensorData] = None
        self._last_imu_input: Optional[SensorData] = None

    def process_pointcloud(self, sensor_data: SensorData) -> PoseEstimate:
        """定位模块接口。"""
        self._ensure_initialized()
        self._validate_sensor_data(sensor_data)
        self._last_pointcloud_input = sensor_data.copy()
        self._pose = self._build_placeholder(sensor_data)
        return self._pose.copy()

    def process_imu(self, sensor_data: SensorData) -> PoseEstimate:
        """定位模块接口。"""
        self._ensure_initialized()
        self._validate_sensor_data(sensor_data)
        self._last_imu_input = sensor_data.copy()
        self._pose = self._build_placeholder(sensor_data)
        return self._pose.copy()

    def process(
        self,
        sensor_data: SensorData,
        adapter_pose: Optional[PoseEstimate] = None,
    ) -> PoseEstimate:
        """定位模块接口。"""
        self._ensure_initialized()
        self._validate_sensor_data(sensor_data)
        if adapter_pose is not None:
            if not isinstance(adapter_pose, PoseEstimate) or not adapter_pose.is_valid():
                raise PoseException(
                    "adapter pose is invalid",
                    code="ADAPTER_POSE_INVALID",
                )
            estimate = adapter_pose.copy()
            estimate.timestamp = float(sensor_data.timestamp)
            estimate.frame_id = self._output_frame_id
            estimate.pose.timestamp = float(sensor_data.timestamp)
            estimate.pose.frame_id = self._output_frame_id
            estimate.source = self._source
            self._pose = estimate
            if self._is_pointcloud(sensor_data):
                self._last_pointcloud_input = sensor_data.copy()
            elif self._is_imu(sensor_data):
                self._last_imu_input = sensor_data.copy()
            return estimate.copy()
        if self._is_pointcloud(sensor_data):
            return self.process_pointcloud(sensor_data)
        if self._is_imu(sensor_data):
            return self.process_imu(sensor_data)
        raise PoseException(
            "unsupported LIO-SAM sensor type",
            code="LIOSAM_SENSOR_TYPE_INVALID",
        )

    def shutdown(self) -> None:
        """定位模块接口。"""
        super().shutdown()
        self._last_pointcloud_input = None
        self._last_imu_input = None

    def _build_placeholder(self, sensor_data: SensorData) -> PoseEstimate:
        """定位模块接口。"""
        timestamp = float(sensor_data.timestamp)
        return PoseEstimate(
            timestamp=timestamp,
            frame_id=self._output_frame_id,
            pose=PoseState(
                timestamp=timestamp,
                frame_id=self._output_frame_id,
            ),
            covariance=(),
            source=self._source,
        )

    @staticmethod
    def _validate_sensor_data(sensor_data: SensorData) -> None:
        """定位模块接口。"""
        if not isinstance(sensor_data, SensorData):
            raise TypeError("sensor_data must be SensorData")
        if not sensor_data.is_valid() or sensor_data.timestamp is None:
            raise PoseException(
                "LIO-SAM sensor data is invalid",
                code="LIOSAM_SENSOR_DATA_INVALID",
            )

    @staticmethod
    def _is_pointcloud(sensor_data: SensorData) -> bool:
        """定位模块接口。"""
        return sensor_data.sensor_type.strip().lower() in {
            "lidar",
            "pointcloud",
            "point_cloud",
            "cloud",
        }

    @staticmethod
    def _is_imu(sensor_data: SensorData) -> bool:
        """定位模块接口。"""
        return sensor_data.sensor_type.strip().lower() in {"imu", "inertial"}
