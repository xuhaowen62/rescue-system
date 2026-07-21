"""幸存者数据模型。"""

from dataclasses import dataclass
from datetime import datetime

from .search_state import SearchState


@dataclass
class Survivor:
    """描述搜救系统中的幸存者及其多模态感知信息。

    Attributes:
        survivor_id: 幸存者的业务唯一标识。
        track_id: 跟踪模块分配的轨迹标识。
        status: 幸存者当前的搜索状态。
        confidence: 当前综合置信度。
        bbox: 图像中的边界框，格式为左、上、右、下。
        image_position: 幸存者在图像坐标系中的位置。
        world_position: 幸存者在世界坐标系中的位置。
        first_seen: 首次发现时间。
        last_seen: 最近一次发现时间。
        frame_count: 累计观测帧数。
        temperature: 热红外观测温度。
        rgb_detected: 是否被可见光传感器检测到。
        thermal_detected: 是否被热红外传感器检测到。
        depth_detected: 是否被深度传感器检测到。
        drone_detected: 是否被无人机检测到。
        ugv_detected: 是否被无人车检测到。
        is_confirmed: 是否已经确认。
        is_rescued: 是否已经完成救援。
        notes: 补充说明。
    """

    survivor_id: str
    track_id: int | None = None
    status: SearchState = SearchState.SEARCHING
    confidence: float = 0.0
    bbox: tuple[float, float, float, float] | None = None
    image_position: tuple[float, float] | None = None
    world_position: tuple[float, float, float] | None = None
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    frame_count: int = 0
    temperature: float | None = None
    rgb_detected: bool = False
    thermal_detected: bool = False
    depth_detected: bool = False
    drone_detected: bool = False
    ugv_detected: bool = False
    is_confirmed: bool = False
    is_rescued: bool = False
    notes: str = ""
