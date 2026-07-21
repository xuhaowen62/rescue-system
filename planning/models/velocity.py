"""速度数据模型。"""

import math
from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping


@dataclass(frozen=True)
class Velocity:
    """表示机器人线速度和角速度。"""

    linear_x: float = 0.0
    linear_y: float = 0.0
    angular_z: float = 0.0
    linear_z: float = 0.0

    def copy(self) -> "Velocity":
        """返回当前速度的独立副本。"""
        return deepcopy(self)

    def is_stopped(self, tolerance: float = 1e-6) -> bool:
        """判断速度是否处于停止范围内。"""
        if not self.is_valid():
            return False
        threshold = max(0.0, float(tolerance))
        return all(
            abs(value) <= threshold
            for value in (
                self.linear_x,
                self.linear_y,
                self.linear_z,
                self.angular_z,
            )
        )

    def is_valid(self) -> bool:
        """判断速度分量是否均为有限数值。"""
        return all(
            math.isfinite(value)
            for value in (
                self.linear_x,
                self.linear_y,
                self.linear_z,
                self.angular_z,
            )
        )

    def to_dict(self) -> Dict[str, Any]:
        """将速度转换为字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Velocity":
        """从字典创建速度。"""
        return cls(
            linear_x=float(data.get("linear_x", 0.0)),
            linear_y=float(data.get("linear_y", 0.0)),
            angular_z=float(data.get("angular_z", 0.0)),
            linear_z=float(data.get("linear_z", 0.0)),
        )
