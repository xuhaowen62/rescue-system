"""定位模块统一时间戳模型。"""

from dataclasses import dataclass
import math
from typing import Union


@dataclass(frozen=True, order=True)
class Timestamp:
    """以秒为内部单位保存时间戳。"""

    seconds: float

    def __post_init__(self) -> None:
        """校验并规范化秒级时间。"""
        value = float(self.seconds)
        if not math.isfinite(value):
            raise ValueError("timestamp must be finite")
        object.__setattr__(self, "seconds", value)

    @classmethod
    def from_milliseconds(cls, value: Union[int, float]) -> "Timestamp":
        """从毫秒创建时间戳。"""
        return cls(float(value) / 1_000.0)

    @classmethod
    def from_nanoseconds(cls, value: Union[int, float]) -> "Timestamp":
        """从纳秒创建时间戳。"""
        return cls(float(value) / 1_000_000_000.0)

    def to_seconds(self) -> float:
        """返回秒级时间。"""
        return self.seconds

    def to_milliseconds(self) -> float:
        """返回毫秒级时间。"""
        return self.seconds * 1_000.0

    def to_nanoseconds(self) -> int:
        """返回四舍五入后的纳秒整数。"""
        return int(round(self.seconds * 1_000_000_000.0))

    def difference(self, other: "Timestamp") -> float:
        """计算当前时间减去另一时间的秒数。"""
        if not isinstance(other, Timestamp):
            raise TypeError("other must be Timestamp")
        return self.seconds - other.seconds

    def __sub__(self, other: "Timestamp") -> float:
        """支持使用减法计算秒级时间差。"""
        return self.difference(other)

    def __float__(self) -> float:
        """转换为秒级浮点数。"""
        return self.seconds
