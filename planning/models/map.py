"""占据栅格地图数据模型。"""

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping, Optional

from planning.models.pose import Pose


@dataclass
class OccupancyGrid:
    """表示规划模块使用的二维占据栅格地图。"""

    width: int = 0
    height: int = 0
    resolution: float = 1.0
    origin: Pose = field(default_factory=Pose)
    data: List[int] = field(default_factory=list)
    timestamp: Optional[float] = None
    frame_id: str = "map"

    def __post_init__(self) -> None:
        """规范化地图数据容器，确保单元格可以被更新。"""
        self.width = int(self.width)
        self.height = int(self.height)
        self.resolution = float(self.resolution)
        self.data = list(self.data)

    def get_cell(self, x: int, y: int) -> int:
        """读取指定栅格坐标的占据值。"""
        return self.data[self._cell_index(x, y)]

    def set_cell(self, x: int, y: int, value: int) -> None:
        """设置指定栅格坐标的占据值。"""
        self.data[self._cell_index(x, y)] = int(value)

    def is_valid(self) -> bool:
        """判断地图尺寸、分辨率和数据长度是否匹配。"""
        return (
            self.width > 0
            and self.height > 0
            and self.resolution > 0.0
            and len(self.data) == self.width * self.height
        )

    def clear(self) -> None:
        """将所有栅格值重置为零，不改变地图尺寸和元数据。"""
        self.data = [0] * max(0, self.width * self.height)

    def copy(self) -> "OccupancyGrid":
        """返回当前地图的独立副本。"""
        return deepcopy(self)

    def to_dict(self) -> Dict[str, Any]:
        """将地图转换为字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "OccupancyGrid":
        """从字典创建占据栅格地图。"""
        origin_data = data.get("origin", {})
        origin = (
            origin_data
            if isinstance(origin_data, Pose)
            else Pose.from_dict(origin_data)
        )
        return cls(
            width=int(data.get("width", 0)),
            height=int(data.get("height", 0)),
            resolution=float(data.get("resolution", 1.0)),
            origin=origin,
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
            raise ValueError("地图数据长度与地图尺寸不一致")
        return index