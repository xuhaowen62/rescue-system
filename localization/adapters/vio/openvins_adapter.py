"""OpenVINS 外部接口的定位适配层。"""

import math
from collections.abc import Mapping, Sequence
from typing import Any, Optional

from localization.adapters.base_adapter import BaseLocalizationAdapter
from localization.exceptions import LocalizationException, PoseException
from localization.models import PoseEstimate, PoseState, SensorData


class OpenVINSAdapter(BaseLocalizationAdapter):
    """提供 Camera/IMU 到统一定位结果的适配接口。

    本类只负责传感器数据校验、类型分发和格式统一，不包含
    OpenVINS 的特征提取、预积分或状态估计算法。
    """

    def __init__(
        self,
        backend: Optional[Any] = None,
        source: str = "openvins-adapter",
    ) -> None:
        """创建 OpenVINS 适配器。"""
        self._backend = backend
        self._source = str(source).strip() or "openvins-adapter"
        self._estimate: Optional[PoseEstimate] = None
        self._initialized = False

    def initialize(self) -> None:
        """初始化适配器及可选的后端接口。"""
        if self._backend is not None and hasattr(self._backend, "initialize"):
            self._backend.initialize()
        self._initialized = True

    def process_sensor_data(self, sensor_data: SensorData) -> PoseEstimate:
        """按传感器类型校验、标准化并转发数据。"""
        self._ensure_initialized()
        data = self._convert_sensor_data(sensor_data)
        sensor_type = data.sensor_type.strip().lower()
        if sensor_type in {"camera", "image", "rgb"}:
            return self.process_image(data)
        if sensor_type in {"imu", "inertial"}:
            return self.process_imu(data)
        raise PoseException(
            "unsupported OpenVINS sensor type",
            code="OPENVINS_SENSOR_TYPE_INVALID",
        )

    def process_image(self, sensor_data: SensorData) -> PoseEstimate:
        """将 CameraData 形式的输入转换为统一图像载荷。"""
        self._ensure_initialized()
        data = self._normalize_camera_data(sensor_data)
        estimate = self._call_backend("process_image", data)
        return self._save_or_build_estimate(estimate, data)

    def process_imu(self, sensor_data: SensorData) -> PoseEstimate:
        """将 ImuData 形式的输入转换为统一 IMU 载荷。"""
        self._ensure_initialized()
        data = self._normalize_imu_data(sensor_data)
        estimate = self._call_backend("process_imu", data)
        return self._save_or_build_estimate(estimate, data)

    def get_pose(self) -> Optional[PoseEstimate]:
        """返回最近一次统一定位结果的副本。"""
        return self._estimate.copy() if self._estimate is not None else None

    def reset(self) -> None:
        """清除适配器缓存并恢复未初始化状态。"""
        self._estimate = None
        self._initialized = False

    def set_backend(self, backend: Optional[Any]) -> None:
        """设置可选的外部算法后端调用对象。"""
        self._backend = backend

    def _call_backend(
        self,
        method_name: str,
        sensor_data: SensorData,
    ) -> Optional[PoseEstimate]:
        """调用后端接口，未接入算法时返回空结果。"""
        if self._backend is None:
            return None
        method = getattr(self._backend, method_name, None)
        if method is None:
            raise LocalizationException(
                "OpenVINS backend interface is incomplete",
                code="OPENVINS_BACKEND_INTERFACE_INVALID",
            )
        result = method(sensor_data)
        if result is not None and not isinstance(result, PoseEstimate):
            raise PoseException(
                "OpenVINS backend result type is invalid",
                code="OPENVINS_RESULT_TYPE_INVALID",
            )
        return result

    def _save_or_build_estimate(
        self,
        estimate: Optional[PoseEstimate],
        sensor_data: SensorData,
    ) -> PoseEstimate:
        """保存后端结果，或生成仅用于接口测试的占位结果。"""
        if estimate is None:
            timestamp = float(sensor_data.timestamp)
            estimate = PoseEstimate(
                timestamp=timestamp,
                frame_id="map",
                pose=PoseState(timestamp=timestamp, frame_id="map"),
                covariance=(),
                source=self._source,
            )
        elif not estimate.is_valid():
            raise PoseException(
                "OpenVINS pose estimate is invalid",
                code="OPENVINS_POSE_INVALID",
            )
        self._estimate = estimate.copy()
        return self._estimate.copy()

    @classmethod
    def _convert_sensor_data(cls, sensor_data: SensorData) -> SensorData:
        """复制并校验统一 SensorData 容器。"""
        data = cls._validate_sensor_data(sensor_data)
        sensor_type = data.sensor_type.strip().lower()
        if sensor_type in {"camera", "image", "rgb"}:
            return cls._normalize_camera_data(data)
        if sensor_type in {"imu", "inertial"}:
            return cls._normalize_imu_data(data)
        return data.copy()

    @staticmethod
    def _validate_sensor_data(sensor_data: SensorData) -> SensorData:
        """校验 OpenVINS 输入边界，不执行传感器算法。"""
        if not isinstance(sensor_data, SensorData):
            raise TypeError("sensor_data must be SensorData")
        if not sensor_data.is_valid() or sensor_data.timestamp is None:
            raise PoseException(
                "sensor data is invalid",
                code="SENSOR_DATA_INVALID",
            )
        if not math.isfinite(float(sensor_data.timestamp)):
            raise PoseException(
                "sensor timestamp is invalid",
                code="SENSOR_TIMESTAMP_INVALID",
            )
        return sensor_data

    @classmethod
    def _normalize_camera_data(cls, sensor_data: SensorData) -> SensorData:
        """生成接近 OpenVINS CameraData 的统一字典载荷。"""
        data = cls._validate_sensor_data(sensor_data)
        payload = data.data
        if isinstance(payload, Mapping):
            image = payload.get("image", payload.get("data"))
            images = payload.get("images")
            images = [image] if images is None else list(images)
            sensor_ids = payload.get("sensor_ids", payload.get("sensor_id", [0]))
            masks = payload.get("masks", payload.get("mask", []))
        else:
            images, sensor_ids, masks = [payload], [0], []
        if images == [None] or not images:
            raise PoseException(
                "camera image data is empty",
                code="OPENVINS_IMAGE_INVALID",
            )
        if isinstance(sensor_ids, int):
            sensor_ids = [sensor_ids]
        sensor_ids = [int(sensor_id) for sensor_id in sensor_ids]
        if len(sensor_ids) != len(images):
            raise PoseException(
                "camera sensor_ids and images size mismatch",
                code="OPENVINS_CAMERA_SIZE_INVALID",
            )
        if masks is None:
            masks = []
        if not isinstance(masks, Sequence) or isinstance(masks, (str, bytes)):
            masks = [masks]
        normalized = {
            "timestamp": float(data.timestamp),
            "sensor_ids": tuple(sensor_ids),
            "images": tuple(images),
            "masks": tuple(masks),
        }
        return SensorData(
            timestamp=float(data.timestamp),
            frame_id=data.frame_id,
            sensor_type="camera",
            data=normalized,
        )

    @classmethod
    def _normalize_imu_data(cls, sensor_data: SensorData) -> SensorData:
        """生成接近 OpenVINS ImuData 的统一字典载荷。"""
        data = cls._validate_sensor_data(sensor_data)
        payload = data.data
        if isinstance(payload, Mapping):
            angular = payload.get("angular_velocity", payload.get("gyro", payload.get("wm")))
            acceleration = payload.get("linear_acceleration", payload.get("accel", payload.get("am")))
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
        angular = cls._validate_vector(angular, "angular velocity")
        acceleration = cls._validate_vector(acceleration, "linear acceleration")
        normalized = {
            "timestamp": float(data.timestamp),
            "wm": angular,
            "am": acceleration,
            "angular_velocity": angular,
            "linear_acceleration": acceleration,
        }
        return SensorData(
            timestamp=float(data.timestamp),
            frame_id=data.frame_id,
            sensor_type="imu",
            data=normalized,
        )

    @staticmethod
    def _validate_vector(value: Any, name: str) -> tuple[float, float, float]:
        """校验三轴向量的长度和有限性。"""
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            raise PoseException(
                f"{name} must contain three values",
                code="OPENVINS_IMU_VECTOR_INVALID",
            )
        values = list(value)
        if len(values) != 3:
            raise PoseException(
                f"{name} must contain three values",
                code="OPENVINS_IMU_VECTOR_INVALID",
            )
        try:
            result = tuple(float(item) for item in values)
        except (TypeError, ValueError) as exc:
            raise PoseException(
                f"{name} contains non-numeric values",
                code="OPENVINS_IMU_VECTOR_INVALID",
            ) from exc
        if not all(math.isfinite(item) for item in result):
            raise PoseException(
                f"{name} contains non-finite values",
                code="OPENVINS_IMU_VECTOR_INVALID",
            )
        return result

    def _ensure_initialized(self) -> None:
        """确保适配器已完成初始化。"""
        if not self._initialized:
            raise LocalizationException(
                "OpenVINS adapter is not initialized",
                code="ADAPTER_NOT_INITIALIZED",
            )
