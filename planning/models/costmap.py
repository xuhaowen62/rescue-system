"""代价地图数据模型。"""

from copy import deepcopy
from dataclasses import asdict, dataclass, field
import math
from typing import Any, Dict, List, Mapping, Optional

from planning.models.map import OccupancyGrid


@dataclass
class CostMap:
    """表示规划模块使用的代价数据容器，不负责计算代价。"""

    width: int = 0
    height: int = 0
    resolution: float = 1.0
    data: List[float] = field(default_factory=list)
    timestamp: Optional[float] = None
    frame_id: str = "map"
    metadata: Mapping[str, Any] = field(default_factory=dict)
    grid: Optional[OccupancyGrid] = None

    def __post_init__(self) -> None:
        """规范化代价数据，并兼容旧版 grid 构造方式。"""
        if self.grid is not None and not self.data:
            self.width = self.grid.width
            self.height = self.grid.height
            if self.resolution == 1.0:
                self.resolution = self.grid.resolution
            self.timestamp = (
                self.grid.timestamp
                if self.timestamp is None
                else self.timestamp
            )
            self.frame_id = (
                self.grid.frame_id
                if self.frame_id == "map"
                else self.frame_id
            )
            self.data = [float(value) for value in self.grid.data]
        self.width = int(self.width)
        self.height = int(self.height)
        self.resolution = float(self.resolution)
        self.data = [float(value) for value in self.data]

    def get_cost(self, x: int, y: int) -> float:
        """读取指定栅格坐标的代价值。"""
        return self.data[self._cell_index(x, y)]

    def set_cost(self, x: int, y: int, value: float) -> None:
        """设置指定栅格坐标的代价值，不执行代价计算。"""
        self.data[self._cell_index(x, y)] = float(value)

    def is_valid(self) -> bool:
        """判断代价地图尺寸、分辨率和数据是否有效。"""
        return (
            self.width > 0
            and self.height > 0
            and self.resolution > 0.0
            and len(self.data) == self.width * self.height
            and all(math.isfinite(value) for value in self.data)
        )

    def clear(self) -> None:
        """将所有代价值重置为零，不执行任何代价处理。"""
        self.data = [0.0] * max(0, self.width * self.height)

    def copy(self) -> "CostMap":
        """返回当前代价地图的独立副本。"""
        return deepcopy(self)

    def to_dict(self) -> Dict[str, Any]:
        """将代价地图转换为字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CostMap":
        """从字典创建代价地图。"""
        grid_data = data.get("grid")
        grid = None
        if grid_data is not None:
            grid = (
                grid_data
                if isinstance(grid_data, OccupancyGrid)
                else OccupancyGrid.from_dict(grid_data)
            )
        return cls(
            width=int(data.get("width", 0)),
            height=int(data.get("height", 0)),
            resolution=float(data.get("resolution", 1.0)),
            data=deepcopy(data.get("data", [])),
            timestamp=data.get("timestamp"),
            frame_id=str(data.get("frame_id", "map")),
            metadata=dict(data.get("metadata", {})),
            grid=grid,
        )

    def _cell_index(self, x: int, y: int) -> int:
        """将二维栅格坐标转换为一维数据索引。"""
        if not 0 <= x < self.width or not 0 <= y < self.height:
            raise IndexError(f"代价坐标越界: ({x}, {y})")
        index = y * self.width + x
        if index >= len(self.data):
            raise ValueError("代价数据长度与地图尺寸不一致")
        return index