"""Traversability 统一输入数据模型。"""

from copy import deepcopy
from dataclasses import asdict, dataclass, field
import math
from typing import Any, Dict, List, Mapping, Optional

from traversability.exceptions import TraversabilityException


@dataclass
class TraversabilityInput:
    """描述一次可通过性分析所需的统一输入数据。"""

    timestamp: Optional[float] = None
    frame_id: str = "map"
    sensor_type: str = "occupancy"
    data: List[float] = field(default_factory=list)
    width: int = 0
    height: int = 0
    resolution: float = 0.0

    def __post_init__(self) -> None:
        """规范化输入字段的基础类型。"""
        if self.timestamp is not None:
            self.timestamp = float(self.timestamp)
        self.frame_id = str(self.frame_id)
        self.sensor_type = str(self.sensor_type).lower()
        self.data = list(self.data)
        self.width = int(self.width)
        self.height = int(self.height)
        self.resolution = float(self.resolution)

    def is_valid(self) -> bool:
        """检查输入元数据和数据长度是否一致且有效。"""
        if self.timestamp is not None:
            if not isinstance(self.timestamp, (int, float)):
                return False
            if not math.isfinite(float(self.timestamp)):
                return False
        if not self.frame_id.strip() or not self.sensor_type.strip():
            return False
        if self.width <= 0 or self.height <= 0:
            return False
        if not math.isfinite(self.resolution) or self.resolution <= 0.0:
            return False
        if len(self.data) != self.width * self.height:
            return False
        return all(
            isinstance(value, (int, float))
            and math.isfinite(float(value))
            for value in self.data
        )

    def reset(self) -> None:
        """清空输入数据并恢复为未初始化状态。"""
        self.timestamp = None
        self.frame_id = ""
        self.sensor_type = ""
        self.data = []
        self.width = 0
        self.height = 0
        self.resolution = 0.0

    def copy(self) -> "TraversabilityInput":
        """返回当前输入的独立副本。"""
        return deepcopy(self)

    def to_dict(self) -> Dict[str, Any]:
        """将输入转换为字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "TraversabilityInput":
        """根据字典创建统一输入对象。"""
        sensor_type = data.get(
            "sensor_type",
            data.get("input_type", "occupancy"),
        )
        return cls(
            timestamp=data.get("timestamp"),
            frame_id=str(data.get("frame_id", "map")),
            sensor_type=str(sensor_type),
            data=deepcopy(data.get("data", [])),
            width=int(data.get("width", 0)),
            height=int(data.get("height", 0)),
            resolution=float(data.get("resolution", 0.0)),
        )

    def validate(self) -> None:
        """校验输入，失败时抛出统一 Traversability 异常。"""
        if not self.is_valid():
            raise TraversabilityException(
                "TraversabilityInput 数据无效",
                code="INPUT_INVALID",
            )
