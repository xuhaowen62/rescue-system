"""Localization 管理器实现。"""

from typing import Optional

from localization.exceptions import LocalizationException, PoseException
from localization.interfaces import BasePoseProvider, BaseSensorProvider
from localization.models import PoseState, SensorData


class LocalizationManager:
    """保存当前位姿并协调传感器与定位提供器的数据流。"""

    def __init__(
        self,
        provider: Optional[BasePoseProvider] = None,
        sensor_provider: Optional[BaseSensorProvider] = None,
    ) -> None:
        """创建管理器并注入可选的数据提供器。"""
        if provider is not None and not isinstance(provider, BasePoseProvider):
            raise TypeError("provider 必须实现 BasePoseProvider")
        if sensor_provider is not None and not isinstance(
            sensor_provider, BaseSensorProvider
        ):
            raise TypeError("sensor_provider 必须实现 BaseSensorProvider")
        self._provider = provider
        self._sensor_provider = sensor_provider
        self._pose: Optional[PoseState] = None
        self._status = "IDLE"

    def set_pose(self, pose: PoseState) -> PoseState:
        """设置当前位姿并返回保存的位姿。"""
        if not isinstance(pose, PoseState):
            raise PoseException("位姿类型无效", code="POSE_TYPE_INVALID")
        if not pose.is_valid():
            raise PoseException("位姿数据无效", code="POSE_DATA_INVALID")
        self._pose = pose.copy()
        self._status = "READY"
        return self._pose.copy()

    def get_pose(self) -> Optional[PoseState]:
        """返回当前位姿的独立副本。"""
        return self._pose.copy() if self._pose is not None else None

    def update_pose(
        self,
        pose: Optional[PoseState] = None,
    ) -> Optional[PoseState]:
        """使用传入位姿或定位提供器更新当前位姿。"""
        if pose is not None:
            return self.set_pose(pose)
        return self.update_from_provider()

    def update_from_provider(self) -> Optional[PoseState]:
        """从定位提供器读取最新位姿并保存到管理器。"""
        if self._provider is None:
            return self.get_pose()
        self._status = "UPDATING"
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
                "位姿提供器更新失败",
                code="PROVIDER_UPDATE_FAILED",
            ) from exc

    def process_sensor_data(
        self,
        sensor_data: Optional[SensorData] = None,
    ) -> Optional[PoseState]:
        """将传感器数据转交给定位提供器并保存返回位姿。"""
        if self._provider is None:
            raise LocalizationException(
                "未设置定位提供器",
                code="PROVIDER_NOT_SET",
            )
        if sensor_data is None:
            if self._sensor_provider is None:
                raise LocalizationException(
                    "未设置传感器数据提供器",
                    code="SENSOR_PROVIDER_NOT_SET",
                )
            sensor_data = self._sensor_provider.update()
        if sensor_data is None:
            self._status = "NO_SENSOR_DATA"
            return None
        if not isinstance(sensor_data, SensorData):
            raise LocalizationException(
                "传感器数据类型无效",
                code="SENSOR_DATA_TYPE_INVALID",
            )
        self._status = "UPDATING"
        try:
            pose = self._provider.process_sensor_data(sensor_data)
            return self.set_pose(pose)
        except PoseException:
            self._status = "FAILED"
            raise
        except Exception as exc:
            self._status = "FAILED"
            raise LocalizationException(
                "传感器数据处理失败",
                code="SENSOR_PROCESS_FAILED",
            ) from exc

    def reset(self) -> None:
        """重置管理器和已注入的数据提供器。"""
        if self._provider is not None:
            self._provider.reset()
        if self._sensor_provider is not None:
            self._sensor_provider.reset()
        self._pose = None
        self._status = "IDLE"

    def get_status(self) -> str:
        """返回当前定位管理状态。"""
        return self._status