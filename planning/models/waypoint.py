"""路径点数据模型。"""

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping

from planning.models.pose import Pose


@dataclass(frozen=True)
class Waypoint:
    """表示路径中的一个带容差目标点。"""

    pose: Pose = field(default_factory=Pose)
    tolerance: float = 0.2
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def copy(self) -> "Waypoint":
        """返回当前路径点的独立副本。"""
        return deepcopy(self)

    def to_dict(self) -> Dict[str, Any]:
        """将路径点转换为字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Waypoint":
        """从字典创建路径点。"""
        pose_data = data.get("pose", {})
        pose = (
            pose_data
            if isinstance(pose_data, Pose)
            else Pose.from_dict(pose_data)
        )
        return cls(
            pose=pose,
            tolerance=float(data.get("tolerance", 0.2)),
            metadata=dict(data.get("metadata", {})),
        )

