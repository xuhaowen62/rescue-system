"""路径数据模型。"""

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping, Optional, Sequence

from planning.models.waypoint import Waypoint


@dataclass(frozen=True, init=False)
class Path:
    """表示规划器输出的路径及其统计信息。"""

    waypoints: Sequence[Waypoint] = field(default_factory=tuple)
    frame_id: str = "map"
    metadata: Mapping[str, Any] = field(default_factory=dict)
    cost: float = 0.0
    length: float = 0.0
    timestamp: Optional[float] = None
    valid: bool = True

    def __init__(
        self,
        waypoints: Sequence[Waypoint] = (),
        frame_id: str = "map",
        metadata: Optional[Mapping[str, Any]] = None,
        cost: float = 0.0,
        length: float = 0.0,
        timestamp: Optional[float] = None,
        is_valid: bool = True,
        valid: Optional[bool] = None,
    ) -> None:
        """创建路径，并兼容 is_valid 参数名。"""
        object.__setattr__(self, "waypoints", waypoints)
        object.__setattr__(self, "frame_id", frame_id)
        object.__setattr__(self, "metadata", metadata or {})
        object.__setattr__(self, "cost", float(cost))
        object.__setattr__(self, "length", float(length))
        object.__setattr__(self, "timestamp", timestamp)
        object.__setattr__(
            self,
            "valid",
            bool(is_valid if valid is None else valid),
        )

    def __repr__(self) -> str:
        """返回便于调试的路径表示。"""
        return (
            "Path("
            f"waypoints={self.waypoints!r}, "
            f"frame_id={self.frame_id!r}, "
            f"cost={self.cost!r}, "
            f"length={self.length!r}, "
            f"is_valid={self.is_valid()!r})"
        )

    def copy(self) -> "Path":
        """返回当前路径的独立副本。"""
        return deepcopy(self)

    def is_valid(self) -> bool:
        """返回路径是否有效。"""
        return self.valid

    def is_completed(self) -> bool:
        """根据路径元数据或进度判断路径是否完成。"""
        if bool(self.metadata.get("completed", False)):
            return True
        return self.get_progress() >= 1.0

    def get_progress(self) -> float:
        """返回路径跟随进度，结果限制在 0 到 1。"""
        try:
            progress = float(self.metadata.get("progress", 0.0))
        except (TypeError, ValueError):
            progress = 0.0
        return max(0.0, min(1.0, progress))

    def to_dict(self) -> Dict[str, Any]:
        """将路径转换为字典。"""
        data = asdict(self)
        data["is_valid"] = data.pop("valid")
        return data

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Path":
        """从字典创建路径。"""
        raw_waypoints = data.get("waypoints", ())
        converted_waypoints = [
            item if isinstance(item, Waypoint) else Waypoint.from_dict(item)
            for item in raw_waypoints
        ]
        waypoints: Sequence[Waypoint]
        waypoints = (
            converted_waypoints
            if isinstance(raw_waypoints, list)
            else tuple(converted_waypoints)
        )
        return cls(
            waypoints=waypoints,
            frame_id=str(data.get("frame_id", "map")),
            metadata=dict(data.get("metadata", {})),
            cost=float(data.get("cost", 0.0)),
            length=float(data.get("length", 0.0)),
            timestamp=data.get("timestamp"),
            is_valid=bool(data.get("is_valid", data.get("valid", True))),
        )
