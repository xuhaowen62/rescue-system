"""Localization 传感器数据模型。"""

from copy import deepcopy
from dataclasses import asdict, dataclass
import math
from typing import Any, Dict, Mapping, Optional


@dataclass
class SensorData:
    """表示传感器输出的统一数据容器。"""

    timestamp: Optional[float] = None
    frame_id: str = "sensor"
    sensor_type: str = ""
    data: Any = None

    def is_valid(self) -> bool:
        """检查传感器数据的基础字段是否有效。"""
        if not self.frame_id or not self.sensor_type or self.data is None:
            return False
        if self.timestamp is None:
            return True
        return isinstance(self.timestamp, (int, float)) and math.isfinite(
            float(self.timestamp)
        )

    def reset(self) -> None:
        """将传感器数据恢复为默认空状态。"""
        self.timestamp = None
        self.frame_id = "sensor"
        self.sensor_type = ""
        self.data = None

    def copy(self) -> "SensorData":
        """返回传感器数据的独立副本。"""
        return SensorData.from_dict(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        """将传感器数据转换为字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SensorData":
        """根据字典创建传感器数据。"""
        timestamp = data.get("timestamp")
        if timestamp is not None:
            timestamp = float(timestamp)
        return cls(
            timestamp=timestamp,
            frame_id=str(data.get("frame_id", "sensor")),
            sensor_type=str(data.get("sensor_type", "")),
            data=deepcopy(data.get("data")),
        )