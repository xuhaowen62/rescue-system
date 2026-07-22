"""传感器时间同步接口。"""

from collections.abc import Sequence
from typing import Dict, List, Optional, Union

from localization.models import SensorData
from localization.utils.time.timestamp import Timestamp


class TimeSynchronizer:
    """提供基于时间窗口的轻量传感器数据同步。"""

    def __init__(
        self,
        tolerance: float = 0.01,
        required_types: Optional[Sequence[str]] = None,
    ) -> None:
        """创建同步器。"""
        self._tolerance = float(tolerance)
        if self._tolerance < 0:
            raise ValueError("tolerance must not be negative")
        self._required_types = (
            tuple(self._normalize_type(item) for item in required_types)
            if required_types
            else None
        )
        self._buffers: Dict[str, List[SensorData]] = {}

    def add_data(
        self,
        sensor_data: Union[SensorData, str],
        sensor_type: Optional[Union[str, SensorData]] = None,
    ) -> None:
        """加入 Camera、IMU 或 LiDAR 数据。"""
        if isinstance(sensor_data, str) and isinstance(sensor_type, SensorData):
            data = sensor_type
            key = self._normalize_type(sensor_data)
        else:
            if not isinstance(sensor_data, SensorData):
                raise TypeError("sensor_data must be SensorData")
            data = sensor_data
            key = self._normalize_type(sensor_type or data.sensor_type)
        if key not in {"camera", "imu", "lidar"}:
            raise ValueError("unsupported sensor type")
        if data.timestamp is None or not data.is_valid():
            raise ValueError("sensor_data must contain a valid timestamp")
        self._buffers.setdefault(key, []).append(data.copy())
        self._buffers[key].sort(key=lambda item: float(item.timestamp))

    def get_synced_data(
        self,
        timestamp: Optional[Union[Timestamp, float]] = None,
        sensor_types: Optional[Sequence[str]] = None,
    ) -> Optional[Dict[str, SensorData]]:
        """返回时间差在容差内的同步数据，不足时返回 None。"""
        keys = (
            tuple(self._normalize_type(item) for item in sensor_types)
            if sensor_types
            else self._required_types or tuple(sorted(self._buffers))
        )
        if not keys or any(key not in self._buffers or not self._buffers[key] for key in keys):
            return None
        target = self._to_seconds(timestamp) if timestamp is not None else min(
            float(self._buffers[key][-1].timestamp) for key in keys
        )
        selected: Dict[str, SensorData] = {}
        times: List[float] = []
        for key in keys:
            item = min(
                self._buffers[key],
                key=lambda value: abs(float(value.timestamp) - target),
            )
            item_time = float(item.timestamp)
            if abs(item_time - target) > self._tolerance:
                return None
            selected[key] = item.copy()
            times.append(item_time)
        if max(times) - min(times) > self._tolerance:
            return None
        return selected

    def clear(self, sensor_type: Optional[str] = None) -> None:
        """清空全部缓存或指定传感器缓存。"""
        if sensor_type is None:
            self._buffers.clear()
            return
        self._buffers.pop(self._normalize_type(sensor_type), None)

    @staticmethod
    def _normalize_type(sensor_type: str) -> str:
        """规范化传感器类型名称。"""
        value = str(sensor_type).strip().lower()
        if value in {"image", "rgb"}:
            return "camera"
        if value in {"inertial"}:
            return "imu"
        if value in {"pointcloud", "point_cloud", "cloud"}:
            return "lidar"
        return value

    @staticmethod
    def _to_seconds(value: Union[Timestamp, float]) -> float:
        """将查询时间转换为秒。"""
        if isinstance(value, Timestamp):
            return value.to_seconds()
        return Timestamp(float(value)).to_seconds()
