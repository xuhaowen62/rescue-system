"""位姿数据模型。"""

from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping, Optional


@dataclass(frozen=True)
class Pose:
    """表示三维位置、姿态角和参考坐标系。"""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    yaw: float = 0.0
    pitch: float = 0.0
    roll: float = 0.0
    frame_id: str = "map"
    timestamp: Optional[float] = None

    def copy(self) -> "Pose":
        """返回当前位姿的独立副本。"""
        return deepcopy(self)

    def to_dict(self) -> Dict[str, Any]:
        """将位姿转换为字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Pose":
        """从字典创建位姿。"""
        return cls(
            x=float(data.get("x", 0.0)),
            y=float(data.get("y", 0.0)),
            z=float(data.get("z", 0.0)),
            yaw=float(data.get("yaw", 0.0)),
            pitch=float(data.get("pitch", 0.0)),
            roll=float(data.get("roll", 0.0)),
            frame_id=str(data.get("frame_id", "map")),
            timestamp=data.get("timestamp"),
        )
