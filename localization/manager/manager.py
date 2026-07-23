"""定位模块的统一接口和数据流处理。"""

from typing import Optional, Union

from localization.adapters import BaseLocalizationAdapter
from localization.core import LocalizationStatus
from localization.backends.base_backend import BaseLocalizationBackend
from localization.exceptions import LocalizationException, PoseException
from localization.interfaces import BasePoseProvider, BaseSensorProvider
from localization.models import PoseEstimate, PoseState, SensorData
from localization.utils.transform import Transform


class LocalizationManager:
    """定位模块的统一接口和数据流处理。"""

    def __init__(
        self,
        provider: Optional[BasePoseProvider] = None,
        sensor_provider: Optional[BaseSensorProvider] = None,
        adapter: Optional[BaseLocalizationAdapter] = None,
        backend: Optional[BaseLocalizationBackend] = None,
    ) -> None:
        """定位模块的统一接口和数据流处理。"""
        if provider is not None and not isinstance(provider, BasePoseProvider):
            raise TypeError("invalid localization state")
        if sensor_provider is not None and not isinstance(
            sensor_provider, BaseSensorProvider
        ):
            raise TypeError("invalid localization state")
        if backend is not None and not isinstance(
            backend, BaseLocalizationBackend
        ):
            raise TypeError("invalid localization backend")
        self._provider = provider
        self._sensor_provider = sensor_provider
        self._adapter: Optional[BaseLocalizationAdapter] = None
        self._backend: Optional[BaseLocalizationBackend] = None
        self._pose: Optional[PoseState] = None
        self._pose_estimate: Optional[PoseEstimate] = None
        self._status = "IDLE"
        if adapter is not None:
            self.set_localization_adapter(adapter)
        if backend is not None:
            self.set_localization_backend(backend)

    def set_localization_adapter(
        self,
        adapter: BaseLocalizationAdapter,
    ) -> None:
        """定位模块的统一接口和数据流处理。"""
        if not isinstance(adapter, BaseLocalizationAdapter):
            raise TypeError("invalid localization state")
        self._adapter = adapter
        self._status = LocalizationStatus.INITIALIZING.value
        try:
            adapter.initialize()
        except Exception as exc:
            self._status = "FAILED"
            raise LocalizationException(
                "adapter initialization failed",
                code="ADAPTER_INITIALIZE_FAILED",
            ) from exc
        self._status = "READY"

    def set_adapter(self, adapter: BaseLocalizationAdapter) -> None:
        """定位模块的统一接口和数据流处理。"""
        self.set_localization_adapter(adapter)

    def get_localization_adapter(
        self,
    ) -> Optional[BaseLocalizationAdapter]:
        """定位模块的统一接口和数据流处理。"""
        return self._adapter

    def set_localization_backend(
        self,
        backend: BaseLocalizationBackend,
    ) -> None:
        """定位模块的统一接口和数据流处理。"""
        if not isinstance(backend, BaseLocalizationBackend):
            raise TypeError("invalid localization backend")
        self._backend = backend
        self._status = LocalizationStatus.INITIALIZING.value
        try:
            backend.initialize()
        except Exception as exc:
            self._status = "FAILED"
            raise LocalizationException(
                "backend initialization failed",
                code="BACKEND_INITIALIZE_FAILED",
            ) from exc
        self._status = "READY"

    def set_backend(self, backend: BaseLocalizationBackend) -> None:
        """定位模块的统一接口和数据流处理。"""
        self.set_localization_backend(backend)

    def get_localization_backend(
        self,
    ) -> Optional[BaseLocalizationBackend]:
        """定位模块的统一接口和数据流处理。"""
        return self._backend

    def get_backend(self) -> Optional[BaseLocalizationBackend]:
        """定位模块的统一接口和数据流处理。"""
        return self.get_localization_backend()

    def set_pose(self, pose: PoseState) -> PoseState:
        """定位模块的统一接口和数据流处理。"""
        if not isinstance(pose, PoseState):
            raise PoseException(
                "pose type is invalid",
                code="POSE_TYPE_INVALID",
            )
        if not pose.is_valid():
            raise PoseException(
                "pose data is invalid",
                code="POSE_DATA_INVALID",
            )
        self._pose = pose.copy()
        self._pose_estimate = PoseEstimate(
            timestamp=pose.timestamp,
            frame_id=pose.frame_id,
            pose=pose,
            source="manager",
        )
        self._status = "READY"
        return self._pose.copy()

    def get_pose(self) -> Optional[PoseState]:
        """定位模块的统一接口和数据流处理。"""
        return self._pose.copy() if self._pose is not None else None

    def get_pose_estimate(self) -> Optional[PoseEstimate]:
        """定位模块的统一接口和数据流处理。"""
        return (
            self._pose_estimate.copy()
            if self._pose_estimate is not None
            else None
        )

    def get_current_pose(self) -> Optional[PoseEstimate]:
        """返回当前统一位姿估计，不暴露具体定位算法实现。"""
        return self.get_pose_estimate()

    def get_localization_state(self) -> str:
        """返回当前定位状态。"""
        return self.get_status()

    def get_transform(self) -> Optional[Transform]:
        """返回 MAP 到当前位姿参考坐标系的变换。"""
        estimate = self.get_current_pose()
        if estimate is None:
            return None
        return Transform(
            parent_frame="map",
            child_frame=estimate.frame_id,
            translation=estimate.position,
            rotation=estimate.orientation_quaternion,
        )

    def update_pose(
        self,
        pose: Optional[PoseState] = None,
    ) -> Optional[PoseState]:
        """定位模块的统一接口和数据流处理。"""
        if pose is not None:
            return self.set_pose(pose)
        return self.update_from_provider()

    def update_from_provider(self) -> Optional[PoseState]:
        """定位模块的统一接口和数据流处理。"""
        if self._provider is None:
            return self.get_pose()
        self._status = LocalizationStatus.RUNNING.value
        try:
            updated_pose = self._provider.update()
            if updated_pose is None:
                self._status = "NO_POSE"
                return None
            return self.set_pose(updated_pose)
        except PoseException:
            self._status = "FAILED"
            raise
        except Exception as exc:
            self._status = "FAILED"
            raise LocalizationException(
                "provider update failed",
                code="PROVIDER_UPDATE_FAILED",
            ) from exc

    def process_sensor_data(
        self,
        sensor_data: Optional[SensorData] = None,
    ) -> Optional[PoseState]:
        """定位模块的统一接口和数据流处理。"""
        if self._backend is not None:
            return self._process_with_backend(sensor_data)
        if self._adapter is not None:
            return self._process_with_adapter(sensor_data)
        return self._process_with_provider(sensor_data)

    def _get_sensor_data(
        self,
        sensor_data: Optional[SensorData],
    ) -> Optional[SensorData]:
        """定位模块的统一接口和数据流处理。"""
        if sensor_data is None:
            if self._sensor_provider is None:
                raise LocalizationException(
                    "sensor provider is not set",
                    code="SENSOR_PROVIDER_NOT_SET",
                )
            sensor_data = self._sensor_provider.update()
        if sensor_data is None:
            self._status = "NO_SENSOR_DATA"
            return None
        if not isinstance(sensor_data, SensorData):
            raise LocalizationException(
                "sensor data type is invalid",
                code="SENSOR_DATA_TYPE_INVALID",
            )
        return sensor_data

    def _validate_estimate(self, estimate: PoseEstimate) -> None:
        """定位模块的统一接口和数据流处理。"""
        if not isinstance(estimate, PoseEstimate):
            raise PoseException(
                "pose estimate type is invalid",
                code="POSE_ESTIMATE_TYPE_INVALID",
            )
        if not estimate.is_valid():
            raise PoseException(
                "pose estimate is invalid",
                code="POSE_ESTIMATE_INVALID",
            )

    def _save_estimate(self, estimate: PoseEstimate) -> PoseState:
        """定位模块的统一接口和数据流处理。"""
        self._pose_estimate = estimate.copy()
        self._pose = estimate.pose.copy()
        self._status = "READY"
        return self._pose.copy()

    def _process_with_adapter(
        self,
        sensor_data: Optional[SensorData],
    ) -> Optional[PoseState]:
        """定位模块的统一接口和数据流处理。"""
        data = self._get_sensor_data(sensor_data)
        if data is None:
            return None
        self._status = LocalizationStatus.RUNNING.value
        try:
            estimate = self._adapter.process_sensor_data(data)
            self._validate_estimate(estimate)
            return self._save_estimate(estimate)
        except PoseException:
            self._status = "FAILED"
            raise
        except Exception as exc:
            self._status = "FAILED"
            raise LocalizationException(
                "adapter processing failed",
                code="ADAPTER_PROCESS_FAILED",
            ) from exc

    def _process_with_backend(
        self,
        sensor_data: Optional[SensorData],
    ) -> Optional[PoseState]:
        """定位模块的统一接口和数据流处理。"""
        if self._adapter is None:
            raise LocalizationException(
                "adapter is not set",
                code="ADAPTER_NOT_SET",
            )
        data = self._get_sensor_data(sensor_data)
        if data is None:
            return None
        self._status = LocalizationStatus.RUNNING.value
        try:
            adapter_estimate = self._adapter.process_sensor_data(data)
            self._validate_estimate(adapter_estimate)
            estimate = self._backend.process(data, adapter_estimate)
            self._validate_estimate(estimate)
            return self._save_estimate(estimate)
        except PoseException:
            self._status = "FAILED"
            raise
        except Exception as exc:
            self._status = "FAILED"
            raise LocalizationException(
                "backend processing failed",
                code="BACKEND_PROCESS_FAILED",
            ) from exc

    def _process_with_provider(
        self,
        sensor_data: Optional[SensorData],
    ) -> Optional[PoseState]:
        """定位模块的统一接口和数据流处理。"""
        if self._provider is None:
            raise LocalizationException(
                "provider is not set",
                code="PROVIDER_NOT_SET",
            )
        data = self._get_sensor_data(sensor_data)
        if data is None:
            return None
        self._status = LocalizationStatus.RUNNING.value
        try:
            pose = self._provider.process_sensor_data(data)
            return self.set_pose(pose)
        except PoseException:
            self._status = "FAILED"
            raise
        except Exception as exc:
            self._status = "FAILED"
            raise LocalizationException(
                "sensor processing failed",
                code="SENSOR_PROCESS_FAILED",
            ) from exc

    def reset(self) -> None:
        """定位模块的统一接口和数据流处理。"""
        if self._backend is not None:
            self._backend.shutdown()
        if self._adapter is not None:
            self._adapter.reset()
        if self._provider is not None:
            self._provider.reset()
        if self._sensor_provider is not None:
            self._sensor_provider.reset()
        self._pose = None
        self._pose_estimate = None
        self._status = "IDLE"

    def set_status(self, status: Union[str, LocalizationStatus]) -> str:
        """设置定位状态，供后端报告跟踪丢失或失败。"""
        value = (
            status.value
            if isinstance(status, LocalizationStatus)
            else str(status).strip().upper()
        )
        allowed = {item.value for item in LocalizationStatus}
        if value not in allowed:
            raise ValueError("invalid localization status")
        self._status = value
        return self._status

    def mark_lost(self) -> None:
        """标记当前定位跟踪已丢失。"""
        self._status = LocalizationStatus.LOST.value

    def get_status(self) -> str:
        """返回当前定位状态。"""
        return self._status
