"""Traversability ??????????"""

from copy import deepcopy
from dataclasses import dataclass, field
import math
from typing import Any, Dict, Optional, Tuple


@dataclass
class SensorData:
    """??????????????????"""

    timestamp: Optional[float] = None
    frame_id: str = "map"
    sensor_type: str = ""
    data: Any = None
    shape: Tuple[int, ...] = field(default_factory=tuple)
    encoding: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """??????????????"""
        if self.timestamp is not None:
            self.timestamp = float(self.timestamp)
        self.frame_id = str(self.frame_id)
        self.sensor_type = str(self.sensor_type).strip().lower()
        self.shape = tuple(int(value) for value in self.shape)
        self.encoding = str(self.encoding).strip()
        self.metadata = dict(self.metadata)

    def is_valid(self) -> bool:
        """???????????????????"""
        if self.timestamp is not None:
            if not math.isfinite(float(self.timestamp)):
                return False
        if not self.frame_id.strip() or not self.sensor_type:
            return False
        if self.data is None or not self.shape:
            return False
        return all(value > 0 for value in self.shape)

    def copy(self) -> "SensorData":
        """????????????"""
        return deepcopy(self)
