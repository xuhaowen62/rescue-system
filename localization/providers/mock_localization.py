"""用于验证传感器到位姿数据流的模拟定位提供器。"""

from typing import Optional

from localization.interfaces import BasePoseProvider
from localization.models import PoseState, SensorData


class MockLocalizationProvider(BasePoseProvider):
    """接收传感器数据并生成简单模拟位姿变化的提供器。"""

    def __init__(self, pose: Optional[PoseState] = None) -> None:
        """创建模拟定位提供器。"""
        if pose is not None and not isinstance(pose, PoseState):
            raise TypeError("pose 必须是 PoseState 实例")
        self._pose = pose.copy() if pose is not None else PoseState()

    def get_pose(self) -> Optional[PoseState]:
        """返回当前模拟位姿。"""
        return self._pose.copy()

    def update(self) -> Optional[PoseState]:
        """返回当前模拟位姿，不执行定位计算。"""
        return self.get_pose()

    def process_sensor_data(self, sensor_data: SensorData) -> PoseState:
        """接收传感器数据并生成一次可重复的模拟位姿变化。"""
        if not isinstance(sensor_data, SensorData):
            raise TypeError("sensor_data 必须是 SensorData 实例")
        if not sensor_data.is_valid():
            raise ValueError("sensor_data 数据无效")
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
        return self._pose.copy()

    def reset(self) -> None:
        """将模拟位姿恢复为默认状态。"""
        self._pose.reset()