"""机器人状态数据模型。"""

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping, Optional

from planning.models.pose import Pose
from planning.models.velocity import Velocity


@dataclass
class RobotState:
    """表示机器人当前的位姿、速度和时间信息。"""

    pose: Pose = field(default_factory=Pose)
    velocity: Velocity = field(default_factory=Velocity)
    timestamp: Optional[float] = None

    def copy(self) -> "RobotState":
        """返回当前机器人状态的独立副本。"""
        return deepcopy(self)

    def update(
        self,
        pose: Optional[Pose] = None,
        velocity: Optional[Velocity] = None,
        timestamp: Optional[float] = None,
    ) -> None:
        """使用非空参数更新机器人状态。"""
        if pose is not None:
            self.pose = pose
        if velocity is not None:
            self.velocity = velocity
        if timestamp is not None:
            self.timestamp = timestamp

    def reset(self) -> None:
        """将机器人状态恢复为默认值。"""
        self.pose = Pose()
        self.velocity = Velocity()
        self.timestamp = None

    def to_dict(self) -> Dict[str, Any]:
        """将机器人状态转换为字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "RobotState":
        """从字典创建机器人状态。"""
        pose_data = data.get("pose", {})
        velocity_data = data.get("velocity", {})
        pose = (
            pose_data
            if isinstance(pose_data, Pose)
            else Pose.from_dict(pose_data)
        )
        velocity = (
            velocity_data
            if isinstance(velocity_data, Velocity)
            else Velocity.from_dict(velocity_data)
        )
        return cls(
            pose=pose,
            velocity=velocity,
            timestamp=data.get("timestamp"),
        )
