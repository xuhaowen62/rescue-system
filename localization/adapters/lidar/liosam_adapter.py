"""定位模块接口。"""

import math
from collections.abc import Mapping, Sequence
from typing import Any, Optional

from localization.adapters.base_adapter import BaseLocalizationAdapter
from localization.exceptions import LocalizationException, PoseException
from localization.models import PoseEstimate, PoseState, SensorData


class LioSAMAdapter(BaseLocalizationAdapter):
    """定位模块接口。"""

    def __init__(
        self,
        backend: Optional[Any] = None,
        source: str = "liosam-adapter",
        output_frame_id: str = "map",
    ) -> None:
        """定位模块接口。"""
        self._backend = backend
        self._source = str(source).strip() or "liosam-adapter"
        self._output_frame_id = str(output_frame_id).strip() or "map"
        self._estimate: Optional[PoseEstimate] = None
        self._initialized = False

    def initialize(self) -> None:
        """定位模块接口。"""
        if self._backend is not None and hasattr(self._backend, "initialize"):
            self._backend.initialize()
        self._initialized = True

    def process_sensor_data(self, sensor_data: SensorData) -> PoseEstimate:
        """定位模块接口。"""
        self._ensure_initialized()
        data = self._validate_sensor_data(sensor_data)
        sensor_type = data.sensor_type.strip().lower()
        if sensor_type in {"lidar", "pointcloud", "point_cloud", "cloud"}:
            return self.process_pointcloud(data)
        if sensor_type in {"imu", "inertial"}:
            return self.process_imu(data)
        raise PoseException(
            "unsupported LIO-SAM sensor type",
            code="LIOSAM_SENSOR_TYPE_INVALID",
        )

    def process_pointcloud(self, sensor_data: SensorData) -> PoseEstimate:
        """定位模块接口。"""
        self._ensure_initialized()
        data = self._normalize_pointcloud_data(sensor_data)
        estimate = self._call_backend("process_pointcloud", data)
        return self._save_or_build_estimate(estimate, data)

    def process_imu(self, sensor_data: SensorData) -> PoseEstimate:
        """定位模块接口。"""
        self._ensure_initialized()
        data = self._normalize_imu_data(sensor_data)
        estimate = self._call_backend("process_imu", data)
        return self._save_or_build_estimate(estimate, data)

    def get_pose(self) -> Optional[PoseEstimate]:
        """定位模块接口。"""
        return self._estimate.copy() if self._estimate is not None else None

    def reset(self) -> None:
        """定位模块接口。"""
        self._estimate = None
        self._initialized = False

    def set_backend(self, backend: Optional[Any]) -> None:
        """定位模块接口。"""
        self._backend = backend

    def _call_backend(
        self,
        method_name: str,
        sensor_data: SensorData,
    ) -> Optional[PoseEstimate]:
        """定位模块接口。"""
        if self._backend is None:
            return None
        method = getattr(self._backend, method_name, None)
        if method is None:
            raise LocalizationException(
                "LIO-SAM backend interface is incomplete",
                code="LIOSAM_BACKEND_INTERFACE_INVALID",
            )
        result = method(sensor_data)
        if result is not None and not isinstance(result, PoseEstimate):
            raise PoseException(
                "LIO-SAM backend result type is invalid",
                code="LIOSAM_RESULT_TYPE_INVALID",
            )
        return result

    def _save_or_build_estimate(
        self,
        estimate: Optional[PoseEstimate],
        sensor_data: SensorData,
    ) -> PoseEstimate:
        """定位模块接口。"""
        if estimate is None:
            timestamp = float(sensor_data.timestamp)
            estimate = PoseEstimate(
                timestamp=timestamp,
                frame_id=self._output_frame_id,
                pose=PoseState(
                    timestamp=timestamp,
                    frame_id=self._output_frame_id,
                ),
                covariance=(),
                source=self._source,
            )
        elif not estimate.is_valid():
            raise PoseException(
                "LIO-SAM pose estimate is invalid",
                code="LIOSAM_POSE_INVALID",
            )
        self._estimate = estimate.copy()
        return self._estimate.copy()

    @staticmethod
    def _validate_sensor_data(sensor_data: SensorData) -> SensorData:
        """定位模块接口。"""
        if not isinstance(sensor_data, SensorData):
            raise TypeError("sensor_data must be SensorData")
        if not sensor_data.is_valid() or sensor_data.timestamp is None:
            raise PoseException(
                "LIO-SAM sensor data is invalid",
                code="LIOSAM_SENSOR_DATA_INVALID",
            )
        if not math.isfinite(float(sensor_data.timestamp)):
            raise PoseException(
                "sensor timestamp is invalid",
                code="LIOSAM_TIMESTAMP_INVALID",
            )
        return sensor_data

    @classmethod
    def _normalize_pointcloud_data(cls, sensor_data: SensorData) -> SensorData:
        """定位模块接口。"""
        data = cls._validate_sensor_data(sensor_data)
        payload = data.data
        if not isinstance(payload, Mapping):
            raise PoseException(
                "LIO-SAM pointcloud data must be a mapping",
                code="LIOSAM_POINTCLOUD_INVALID",
            )
        points = payload.get("points", payload.get("pointcloud", payload.get("cloud")))
        point_time = payload.get("point_time", payload.get("time"))
        ring = payload.get("ring", payload.get("rings"))
        points = cls._to_sequence(points, "points")
        point_time = cls._to_sequence(point_time, "point_time")
        ring = cls._to_sequence(ring, "ring")
        if not points:
            raise PoseException(
                "LIO-SAM pointcloud is empty",
                code="LIOSAM_POINTCLOUD_EMPTY",
            )
        if len(point_time) != len(points) or len(ring) != len(points):
            raise PoseException(
                "pointcloud fields have different sizes",
                code="LIOSAM_POINTCLOUD_SIZE_INVALID",
            )
        try:
            normalized_time = tuple(float(value) for value in point_time)
            normalized_ring = tuple(int(value) for value in ring)
        except (TypeError, ValueError) as exc:
            raise PoseException(
                "pointcloud time or ring contains invalid values",
                code="LIOSAM_POINTCLOUD_FIELD_INVALID",
            ) from exc
        if not all(math.isfinite(value) for value in normalized_time):
            raise PoseException(
                "pointcloud time contains non-finite values",
                code="LIOSAM_POINT_TIME_INVALID",
            )
        normalized = {
            "points": tuple(points),
            "point_time": normalized_time,
            "ring": normalized_ring,
            "time": normalized_time,
            "rings": normalized_ring,
        }
        return SensorData(
            timestamp=float(data.timestamp),
            frame_id=data.frame_id,
            sensor_type="lidar",
            data=normalized,
        )

    @classmethod
    def _normalize_imu_data(cls, sensor_data: SensorData) -> SensorData:
        """定位模块接口。"""
        data = cls._validate_sensor_data(sensor_data)
        payload = data.data
        if isinstance(payload, Mapping):
            angular = payload.get(
                "angular_velocity", payload.get("gyro", payload.get("wm"))
            )
            acceleration = payload.get(
                "linear_acceleration", payload.get("accel", payload.get("am"))
            )
        elif isinstance(payload, Sequence) and not isinstance(payload, (str, bytes)):
            values = list(payload)
            if len(values) == 6:
                angular, acceleration = values[:3], values[3:]
            elif len(values) == 3:
                angular, acceleration = values, (0.0, 0.0, 0.0)
            else:
                angular = acceleration = None
        else:
            angular = acceleration = None
        angular = cls._validate_vector(angular, "angular_velocity")
        acceleration = cls._validate_vector(acceleration, "linear_acceleration")
        normalized = {
            "angular_velocity": angular,
            "linear_acceleration": acceleration,
            "gyro": angular,
            "accel": acceleration,
        }
        return SensorData(
            timestamp=float(data.timestamp),
            frame_id=data.frame_id,
            sensor_type="imu",
            data=normalized,
        )

    @staticmethod
    def _to_sequence(value: Any, name: str) -> list[Any]:
        """定位模块接口。"""
        if value is None or isinstance(value, (str, bytes)):
            raise PoseException(
                f"LIO-SAM {name} is missing",
                code="LIOSAM_POINTCLOUD_FIELD_MISSING",
            )
        if isinstance(value, Mapping):
            raise PoseException(
                f"LIO-SAM {name} must be a sequence",
                code="LIOSAM_POINTCLOUD_FIELD_INVALID",
            )
        try:
            return list(value)
        except TypeError as exc:
            raise PoseException(
                f"LIO-SAM {name} must be a sequence",
                code="LIOSAM_POINTCLOUD_FIELD_INVALID",
            ) from exc

    @staticmethod
    def _validate_vector(value: Any, name: str) -> tuple[float, float, float]:
        """定位模块接口。"""
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            raise PoseException(
                f"{name} must contain three values",
                code="LIOSAM_IMU_VECTOR_INVALID",
            )
        values = list(value)
        if len(values) != 3:
            raise PoseException(
                f"{name} must contain three values",
                code="LIOSAM_IMU_VECTOR_INVALID",
            )
        try:
            result = tuple(float(item) for item in values)
        except (TypeError, ValueError) as exc:
            raise PoseException(
                f"{name} contains non-numeric values",
                code="LIOSAM_IMU_VECTOR_INVALID",
            ) from exc
        if not all(math.isfinite(item) for item in result):
            raise PoseException(
                f"{name} contains non-finite values",
                code="LIOSAM_IMU_VECTOR_INVALID",
            )
        return result

    def _ensure_initialized(self) -> None:
        """定位模块接口。"""
        if not self._initialized:
            raise LocalizationException(
                "LIO-SAM adapter is not initialized",
                code="ADAPTER_NOT_INITIALIZED",
            )
