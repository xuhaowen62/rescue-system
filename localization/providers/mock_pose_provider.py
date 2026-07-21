"""用于验证定位数据流的模拟位姿提供器。"""

from typing import Optional

from localization.interfaces import BasePoseProvider
from localization.models import PoseState, SensorData


class MockPoseProvider(BasePoseProvider):
    """返回固定默认位姿的模拟提供器，不包含定位算法。"""

    def __init__(self, pose: Optional[PoseState] = None) -> None:
        """创建模拟提供器。"""
        if pose is not None and not isinstance(pose, PoseState):
            raise TypeError("pose 必须是 PoseState 实例")
        self._pose = pose.copy() if pose is not None else PoseState()

    def get_pose(self) -> Optional[PoseState]:
        """返回当前模拟位姿。"""
        return self._pose.copy()

    def update(self) -> Optional[PoseState]:
        """返回一次模拟更新结果。"""
        return self.get_pose()

    def process_sensor_data(self, sensor_data: SensorData) -> PoseState:
        """接收传感器数据并返回当前模拟位姿。"""
        if not isinstance(sensor_data, SensorData):
            raise TypeError("sensor_data 必须是 SensorData 实例")
        return self._pose.copy()

    def reset(self) -> None:
        """将模拟位姿恢复为默认状态。"""
        self._pose.reset()