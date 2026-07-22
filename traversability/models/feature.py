"""可通过性多模态处理模块。"""

from copy import deepcopy
from dataclasses import dataclass, field
import math
from typing import Any, Dict, Optional, Tuple


@dataclass
class FeatureRepresentation:
    """定义本模块的统一接口或数据结构。"""

    sensor_type: str = ""
    timestamp: Optional[float] = None
    frame_id: str = "map"
    feature_data: Any = None
    shape: Tuple[int, ...] = field(default_factory=tuple)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """执行本模块定义的标准处理步骤。"""
        self.sensor_type = str(self.sensor_type).strip().lower()
        if self.timestamp is not None:
            self.timestamp = float(self.timestamp)
        self.frame_id = str(self.frame_id)
        self.shape = tuple(int(value) for value in self.shape)
        self.metadata = dict(self.metadata)

    def is_valid(self) -> bool:
        """执行本模块定义的标准处理步骤。"""
        if not self.sensor_type or not self.frame_id.strip():
            return False
        if self.timestamp is not None and not math.isfinite(
            float(self.timestamp)
        ):
            return False
        if self.feature_data is None or not self.shape:
            return False
        return all(value > 0 for value in self.shape)

    def copy(self) -> "FeatureRepresentation":
        """执行本模块定义的标准处理步骤。"""
        return deepcopy(self)
