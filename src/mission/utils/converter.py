"""Mission 与 Tracking 之间的数据转换工具。"""

from collections.abc import Iterable, Mapping
from dataclasses import asdict
from datetime import datetime
from typing import TYPE_CHECKING, List

from ..models.search_state import SearchState
from ..models.survivor import Survivor

if TYPE_CHECKING:
    from perception.tracking.bytetrack import STrack


def track_to_survivor(track: "STrack") -> Survivor:
    """将单条 Tracking 轨迹转换为 Survivor。

    Args:
        track: Tracking 模块输出的单条轨迹。

    Returns:
        转换后的幸存者模型。
    """
    now = datetime.now()
    track_id = int(track.track_id)
    bbox = _get_bbox(track)
    return Survivor(
        survivor_id=str(track_id),
        track_id=track_id,
        status=_get_status(track),
        confidence=float(track.score),
        bbox=bbox,
        image_position=((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2),
        first_seen=_get_seen_time(track, "first_seen", now),
        last_seen=_get_seen_time(track, "last_seen", now),
        frame_count=_get_frame_count(track),
    )


def tracks_to_survivors(tracks: List["STrack"]) -> List[Survivor]:
    """将多条 Tracking 轨迹转换为 Survivor 列表。

    Args:
        tracks: Tracking 模块输出的轨迹列表。

    Returns:
        转换后的幸存者列表。
    """
    return [track_to_survivor(track) for track in tracks]


def survivor_to_dict(survivor: Survivor) -> dict[str, object]:
    """将 Survivor 转换为适合保存的字典。

    Args:
        survivor: 待转换的幸存者模型。

    Returns:
        包含幸存者字段的字典。
    """
    data = asdict(survivor)
    data["status"] = survivor.status.value
    for key in ("first_seen", "last_seen"):
        value = data[key]
        if isinstance(value, datetime):
            data[key] = value.isoformat()
    return data


def dict_to_survivor(data: Mapping[str, object]) -> Survivor:
    """将保存的字典恢复为 Survivor。

    Args:
        data: 包含幸存者字段的数据字典。

    Returns:
        恢复后的幸存者模型。

    Raises:
        ValueError: 数据中的状态或坐标格式不正确。
        TypeError: 数据中的时间或坐标类型不正确。
    """
    raw_status = data.get("status", SearchState.SEARCHING)
    status = _parse_status(raw_status)
    track_id = data.get("track_id")
    return Survivor(
        survivor_id=str(data["survivor_id"]),
        track_id=None if track_id is None else int(track_id),
        status=status,
        confidence=float(data.get("confidence", 0.0)),
        bbox=_parse_position(data.get("bbox"), 4),
        image_position=_parse_position(data.get("image_position"), 2),
        world_position=_parse_position(data.get("world_position"), 3),
        first_seen=_parse_datetime(data.get("first_seen")),
        last_seen=_parse_datetime(data.get("last_seen")),
        frame_count=int(data.get("frame_count", 0)),
        temperature=_parse_optional_float(data.get("temperature")),
        rgb_detected=bool(data.get("rgb_detected", False)),
        thermal_detected=bool(data.get("thermal_detected", False)),
        depth_detected=bool(data.get("depth_detected", False)),
        drone_detected=bool(data.get("drone_detected", False)),
        ugv_detected=bool(data.get("ugv_detected", False)),
        is_confirmed=bool(data.get("is_confirmed", False)),
        is_rescued=bool(data.get("is_rescued", False)),
        notes=str(data.get("notes", "")),
    )


def _get_bbox(track: object) -> tuple[float, float, float, float]:
    """读取轨迹的边界框并转换为标准元组。"""
    raw_bbox = getattr(track, "tlbr")
    values = tuple(float(value) for value in raw_bbox)
    if len(values) != 4:
        raise ValueError("轨迹边界框必须包含四个坐标值。")
    return (values[0], values[1], values[2], values[3])


def _get_status(track: object) -> SearchState:
    """根据轨迹状态生成 Mission 搜索状态。"""
    state = getattr(track, "state", None)
    state_name = getattr(state, "name", str(state))
    state_mapping = {
        "Tracked": SearchState.TRACKING,
        "Lost": SearchState.SEARCHING,
        "Removed": SearchState.FINISHED,
    }
    return state_mapping.get(state_name, SearchState.TRACKING)


def _get_seen_time(track: object, name: str, fallback: datetime) -> datetime:
    """读取轨迹时间字段，不存在时使用当前时间。"""
    value = getattr(track, name, None)
    return value if isinstance(value, datetime) else fallback


def _get_frame_count(track: object) -> int:
    """读取轨迹累计观测帧数。"""
    tracklet_len = getattr(track, "tracklet_len", None)
    if tracklet_len is not None:
        return max(0, int(tracklet_len))
    frame_id = getattr(track, "frame_id", None)
    start_frame = getattr(track, "start_frame", None)
    if frame_id is None or start_frame is None:
        return 0
    return max(0, int(frame_id) - int(start_frame) + 1)


def _parse_status(value: object) -> SearchState:
    """将字典中的状态值转换为 SearchState。"""
    if isinstance(value, SearchState):
        return value
    try:
        return SearchState(str(value))
    except ValueError as error:
        raise ValueError("无效的幸存者状态。") from error


def _parse_datetime(value: object) -> datetime | None:
    """将字典中的时间值转换为 datetime。"""
    if value is None or isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError as error:
            raise ValueError("无效的时间格式。") from error
    raise TypeError("时间字段必须是字符串、datetime 或 None。")


def _parse_position(
    value: object,
    size: int,
) -> tuple[float, ...] | None:
    """将字典中的坐标值转换为指定长度的浮点元组。"""
    if value is None:
        return None
    if isinstance(value, (str, bytes)) or not isinstance(value, Iterable):
        raise TypeError("坐标字段必须是可迭代数值。")
    values = tuple(float(item) for item in value)
    if len(values) != size:
        raise ValueError("坐标字段长度不符合要求。")
    return values


def _parse_optional_float(value: object) -> float | None:
    """将可选数值转换为浮点数。"""
    return None if value is None else float(value)
