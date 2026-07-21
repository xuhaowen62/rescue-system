"""区域可通过性网格数据模型。"""

from copy import deepcopy
from dataclasses import asdict, dataclass, field
import math
from typing import Any, Dict, List, Mapping, Optional


@dataclass
class TraversabilityGrid:
    """表示每个栅格单元可通过性结果的数据容器。"""

    width: int = 0
    height: int = 0
    resolution: float = 1.0
    data: List[float] = field(default_factory=list)
    timestamp: Optional[float] = None
    frame_id: str = "map"

    def __post_init__(self) -> None:
        """规范化网格尺寸、分辨率和单元数据类型。"""
        self.width = int(self.width)
        self.height = int(self.height)
        self.resolution = float(self.resolution)
        self.data = [float(value) for value in self.data]

    def get_value(self, x: int, y: int) -> float:
        """读取指定栅格坐标的可通过性值。"""
        return self.data[self._cell_index(x, y)]

    def set_value(self, x: int, y: int, value: float) -> None:
        """设置指定栅格坐标的可通过性值。"""
        numeric_value = float(value)
        if not math.isfinite(numeric_value) or not 0.0 <= numeric_value <= 1.0:
            raise ValueError("可通过性值必须位于 0.0 到 1.0 之间")
        self.data[self._cell_index(x, y)] = numeric_value

    def is_valid(self) -> bool:
        """检查网格尺寸、分辨率和可通过性数据是否有效。"""
        if (
            self.width <= 0
            or self.height <= 0
            or self.resolution <= 0.0
            or len(self.data) != self.width * self.height
            or not self.frame_id
        ):
            return False
        if self.timestamp is not None:
            if not isinstance(self.timestamp, (int, float)):
                return False
            if not math.isfinite(float(self.timestamp)):
                return False
        return all(
            math.isfinite(value) and 0.0 <= value <= 1.0
            for value in self.data
        )

    def clear(self) -> None:
        """将所有可通过性结果重置为零并保留网格尺寸。"""
        self.data = [0.0] * max(0, self.width * self.height)

    def copy(self) -> "TraversabilityGrid":
        """返回当前网格的独立副本。"""
        return deepcopy(self)

    def to_dict(self) -> Dict[str, Any]:
        """将网格转换为字典。"""
        return asdict(self)

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "TraversabilityGrid":
        """根据字典创建可通过性网格。"""
        return cls(
            width=int(data.get("width", 0)),
            height=int(data.get("height", 0)),
            resolution=float(data.get("resolution", 1.0)),
            data=deepcopy(data.get("data", [])),
            timestamp=data.get("timestamp"),
            frame_id=str(data.get("frame_id", "map")),
        )

    def _cell_index(self, x: int, y: int) -> int:
        """将二维栅格坐标转换为一维数据索引。"""
        if not 0 <= x < self.width or not 0 <= y < self.height:
            raise IndexError(f"栅格坐标越界: ({x}, {y})")
        index = y * self.width + x
        if index >= len(self.data):
            raise ValueError("网格数据长度与网格尺寸不一致")
        return index