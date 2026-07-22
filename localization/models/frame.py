"""定位坐标系定义。"""

from enum import Enum
from typing import Tuple


class CoordinateFrame(str, Enum):
    """定义定位模块统一使用的坐标系名称。"""

    MAP = "map"
    ODOM = "odom"
    BASE_LINK = "base_link"
    IMU = "imu"
    CAMERA = "camera"
    LIDAR = "lidar"

    @classmethod
    def from_value(cls, value: str) -> "CoordinateFrame":
        """根据字符串创建坐标系枚举。"""
        normalized = str(value).strip().lower()
        for item in cls:
            if item.value == normalized or item.name.lower() == normalized:
                return item
        raise ValueError("unsupported coordinate frame")

    @classmethod
    def chain(cls, platform: str = "ugv") -> Tuple["CoordinateFrame", ...]:
        """返回无人车或无人机的基础坐标系链。"""
        normalized = str(platform).strip().lower()
        if normalized not in {"ugv", "uav"}:
            raise ValueError("platform must be ugv or uav")
        if normalized == "ugv":
            return (cls.MAP, cls.ODOM, cls.BASE_LINK, cls.LIDAR, cls.IMU)
        return (cls.MAP, cls.ODOM, cls.BASE_LINK, cls.CAMERA, cls.IMU, cls.LIDAR)

    @classmethod
    def parent_of(
        cls,
        frame: "CoordinateFrame",
        platform: str = "ugv",
    ) -> "CoordinateFrame":
        """返回指定平台中坐标系的直接父坐标系。"""
        chain = cls.chain(platform)
        frame = cls.from_value(frame.value if isinstance(frame, cls) else str(frame))
        index = chain.index(frame)
        if index == 0:
            raise ValueError("map frame has no parent")
        return chain[index - 1]
