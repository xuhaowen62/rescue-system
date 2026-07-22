"""定位模块扩展接口。"""

from typing import Optional

from localization.exceptions import LocalizationException, PoseException
from localization.models import PoseEstimate, PoseState, SensorData
from localization.adapters.base_adapter import BaseLocalizationAdapter


class MockLocalizationAdapter(BaseLocalizationAdapter):
    """定义本模块的统一接口或数据结构。"""

    def __init__(
        self,
        pose: Optional[PoseState] = None,
        source: str = "mock",
    ) -> None:
        """定义本模块的统一接口或数据结构。"""
        if pose is not None and not isinstance(pose, PoseState):
            raise TypeError("invalid localization input")
        self._pose = pose.copy() if pose is not None else PoseState()
        self._source = str(source).strip() or "mock"
        self._estimate: Optional[PoseEstimate] = None
        self._initialized = False

    def initialize(self) -> None:
        """执行本模块定义的标准处理步骤。"""
        self._initialized = True

    def process_sensor_data(self, sensor_data: SensorData) -> PoseEstimate:
        """执行本模块定义的标准处理步骤。"""
        if not self._initialized:
            raise LocalizationException(
                "invalid localization input",
                code="ADAPTER_NOT_INITIALIZED",
            )
        if not isinstance(sensor_data, SensorData):
            raise TypeError("invalid localization input")
        if not sensor_data.is_valid():
            raise PoseException(
                "invalid localization input",
                code="SENSOR_DATA_INVALID",
            )
        self._pose = PoseState(
            x=self._pose.x + 1.0,
            y=self._pose.y,
            z=self._pose.z,
            roll=self._pose.roll,
            pitch=self._pose.pitch,
            yaw=self._pose.yaw,
            timestamp=sensor_data.timestamp,
            frame_id=self._pose.frame_id,
        )
        timestamp = sensor_data.timestamp
        if timestamp is None:
            timestamp = 0.0
        self._estimate = PoseEstimate(
            timestamp=timestamp,
            frame_id=self._pose.frame_id,
            pose=self._pose,
            covariance=(),
            source=self._source,
        )
        return self._estimate.copy()

    def get_pose(self) -> Optional[PoseEstimate]:
        """执行本模块定义的标准处理步骤。"""
        return self._estimate.copy() if self._estimate is not None else None

    def reset(self) -> None:
        """执行本模块定义的标准处理步骤。"""
        self._pose.reset()
        self._estimate = None
        self._initialized = False
