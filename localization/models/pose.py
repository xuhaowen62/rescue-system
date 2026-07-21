"""Localization 位姿数据模型。"""

from dataclasses import asdict, dataclass
import math
from typing import Any, Dict, Mapping, Optional


@dataclass
class PoseState:
    """表示定位模块输出的三维位姿状态。"""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0
    timestamp: Optional[float] = None
    frame_id: str = "map"

    def distance_to(self, other: "PoseState") -> float:
        """计算当前位姿与另一位姿之间的位置欧氏距离。"""
        if not isinstance(other, PoseState):
            raise TypeError("other 必须是 PoseState 实例")
        return math.sqrt(
            (self.x - other.x) ** 2
            + (self.y - other.y) ** 2
            + (self.z - other.z) ** 2
        )

    def reset(self) -> None:
        """将位姿恢复为默认状态。"""
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.timestamp = None
        self.frame_id = "map"

    def is_valid(self) -> bool:
        """检查位置、姿态和时间戳是否为有效有限数值。"""
        values = (self.x, self.y, self.z, self.roll, self.pitch, self.yaw)
        if not all(isinstance(value, (int, float)) for value in values):
            return False
        if not all(math.isfinite(float(value)) for value in values):
            return False
        if self.timestamp is not None:
            if not isinstance(self.timestamp, (int, float)):
                return False
            if not math.isfinite(float(self.timestamp)):
                return False
        return bool(self.frame_id)

    def copy(self) -> "PoseState":
        """返回当前位姿的独立副本。"""
        return PoseState.from_dict(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        """将位姿转换为字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PoseState":
        """根据字典创建位姿。"""
        return cls(
            x=float(data.get("x", 0.0)),
            y=float(data.get("y", 0.0)),
            z=float(data.get("z", 0.0)),
            roll=float(data.get("roll", 0.0)),
            pitch=float(data.get("pitch", 0.0)),
            yaw=float(data.get("yaw", 0.0)),
            timestamp=data.get("timestamp"),
            frame_id=str(data.get("frame_id", "map")),
        )