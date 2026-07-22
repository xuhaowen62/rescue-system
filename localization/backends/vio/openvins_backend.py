"""OpenVINS 外部算法的后端适配占位。"""

from typing import Any, Optional

from localization.backends.external.vio_backend import VIOBackend
from localization.exceptions import PoseException
from localization.models import PoseEstimate, PoseState, SensorData


class OpenVINSBackend(VIOBackend):
    """保留 OpenVINS 调用边界，但不实现 VIO 算法。"""

    def __init__(self, **parameters: Any) -> None:
        """创建 OpenVINS 后端适配对象。"""
        super().__init__(**parameters)
        self._source = str(parameters.get("source", "openvins")).strip() or "openvins"
        self._last_camera_input: Optional[SensorData] = None
        self._last_imu_input: Optional[SensorData] = None

    def process_image(self, sensor_data: SensorData) -> PoseEstimate:
        """接收 CameraData 边界输入，返回统一占位结果。"""
        self._ensure_initialized()
        self._validate_openvins_sensor_data(sensor_data)
        self._last_camera_input = sensor_data.copy()
        self._pose = self._build_placeholder(sensor_data)
        return self._pose.copy()

    def process_imu(self, sensor_data: SensorData) -> PoseEstimate:
        """接收 ImuData 边界输入，返回统一占位结果。"""
        self._ensure_initialized()
        self._validate_openvins_sensor_data(sensor_data)
        self._last_imu_input = sensor_data.copy()
        self._pose = self._build_placeholder(sensor_data)
        return self._pose.copy()

    def process(
        self,
        sensor_data: SensorData,
        adapter_pose: Optional[PoseEstimate] = None,
    ) -> PoseEstimate:
        """提供 LocalizationManager 使用的通用后端调用入口。"""
        self._ensure_initialized()
        self._validate_openvins_sensor_data(sensor_data)
        if adapter_pose is not None:
            if not isinstance(adapter_pose, PoseEstimate):
                raise TypeError("adapter_pose must be PoseEstimate")
            if not adapter_pose.is_valid():
                raise PoseException(
                    "adapter pose is invalid",
                    code="ADAPTER_POSE_INVALID",
                )
            estimate = adapter_pose.copy()
            estimate.source = self._source
            estimate.timestamp = float(sensor_data.timestamp)
            estimate.pose.timestamp = float(sensor_data.timestamp)
            self._pose = estimate
            return estimate.copy()
        if sensor_data.sensor_type.strip().lower() in {"camera", "image", "rgb"}:
            return self.process_image(sensor_data)
        return self.process_imu(sensor_data)

    def shutdown(self) -> None:
        """清理接口状态，不执行外部算法关闭逻辑。"""
        super().shutdown()
        self._last_camera_input = None
        self._last_imu_input = None

    @staticmethod
    def _validate_openvins_sensor_data(sensor_data: SensorData) -> None:
        """校验后端需要的带时间戳传感器输入。"""
        if not isinstance(sensor_data, SensorData):
            raise TypeError("sensor_data must be SensorData")
        if not sensor_data.is_valid() or sensor_data.timestamp is None:
            raise PoseException(
                "OpenVINS sensor data is invalid",
                code="OPENVINS_SENSOR_DATA_INVALID",
            )

    def _build_placeholder(self, sensor_data: SensorData) -> PoseEstimate:
        """生成表示接口可用性的身份位姿，不进行算法估计。"""
        timestamp = float(sensor_data.timestamp)
        return PoseEstimate(
            timestamp=timestamp,
            frame_id="map",
            pose=PoseState(timestamp=timestamp, frame_id="map"),
            covariance=(),
            source=self._source,
        )
