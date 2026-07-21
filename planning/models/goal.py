"""规划目标数据模型。"""

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping, Optional

from planning.models.pose import Pose


@dataclass(frozen=True)
class Goal:
    """表示规划模块需要到达的目标位姿。"""

    pose: Pose = field(default_factory=Pose)
    target_id: str = ""
    tolerance: float = 0.2
    yaw_tolerance: float = 0.1
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def position_tolerance(self) -> float:
        """返回位置容差兼容值。"""
        return self.tolerance

    @property
    def goal_id(self) -> str:
        """返回目标编号兼容值。"""
        return self.target_id

    def copy(self) -> "Goal":
        """返回当前目标的独立副本。"""
        return deepcopy(self)

    def to_dict(self) -> Dict[str, Any]:
        """将目标转换为字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Goal":
        """从字典创建目标。"""
        pose_data = data.get("pose", {})
        pose = (
            pose_data
            if isinstance(pose_data, Pose)
            else Pose.from_dict(pose_data)
        )
        target_id = data.get("target_id", data.get("goal_id", ""))
        tolerance = data.get(
            "tolerance",
            data.get("position_tolerance", 0.2),
        )
        return cls(
            pose=pose,
            target_id=str(target_id),
            tolerance=float(tolerance),
            yaw_tolerance=float(data.get("yaw_tolerance", 0.1)),
            metadata=dict(data.get("metadata", {})),
        )

