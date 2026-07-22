"""定位模块统一四元数工具。"""

from dataclasses import dataclass
import math
from typing import Sequence, Tuple, Union


@dataclass(frozen=True)
class Quaternion:
    """以 x、y、z、w 顺序保存姿态四元数。"""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 1.0

    def __post_init__(self) -> None:
        """校验四元数分量。"""
        values = tuple(float(value) for value in (self.x, self.y, self.z, self.w))
        if not all(math.isfinite(value) for value in values):
            raise ValueError("quaternion values must be finite")
        object.__setattr__(self, "x", values[0])
        object.__setattr__(self, "y", values[1])
        object.__setattr__(self, "z", values[2])
        object.__setattr__(self, "w", values[3])

    @classmethod
    def identity(cls) -> "Quaternion":
        """返回单位四元数。"""
        return cls(0.0, 0.0, 0.0, 1.0)

    def normalize(self) -> "Quaternion":
        """返回归一化后的四元数。"""
        norm = math.sqrt(self.x**2 + self.y**2 + self.z**2 + self.w**2)
        if norm == 0.0:
            raise ValueError("zero quaternion cannot be normalized")
        return Quaternion(self.x / norm, self.y / norm, self.z / norm, self.w / norm)

    def inverse(self) -> "Quaternion":
        """返回单位四元数的逆。"""
        normalized = self.normalize()
        return Quaternion(-normalized.x, -normalized.y, -normalized.z, normalized.w)

    def __mul__(self, other: "Quaternion") -> "Quaternion":
        """组合两个旋转。"""
        if not isinstance(other, Quaternion):
            raise TypeError("other must be Quaternion")
        return Quaternion(
            self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y,
            self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x,
            self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w,
            self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z,
        ).normalize()

    def rotate_vector(self, vector: Sequence[float]) -> Tuple[float, float, float]:
        """使用当前旋转变换三维向量，并保持向量长度。"""
        if len(vector) != 3:
            raise ValueError("vector must contain three values")
        q = self.normalize()
        vx, vy, vz = (float(value) for value in vector)
        tx = 2.0 * (q.y * vz - q.z * vy)
        ty = 2.0 * (q.z * vx - q.x * vz)
        tz = 2.0 * (q.x * vy - q.y * vx)
        return (
            vx + q.w * tx + q.y * tz - q.z * ty,
            vy + q.w * ty + q.z * tx - q.x * tz,
            vz + q.w * tz + q.x * ty - q.y * tx,
        )

    @staticmethod
    def euler_to_quaternion(
        roll: float,
        pitch: float,
        yaw: float,
    ) -> "Quaternion":
        """将欧拉角转换为四元数。"""
        cr = math.cos(float(roll) / 2.0)
        sr = math.sin(float(roll) / 2.0)
        cp = math.cos(float(pitch) / 2.0)
        sp = math.sin(float(pitch) / 2.0)
        cy = math.cos(float(yaw) / 2.0)
        sy = math.sin(float(yaw) / 2.0)
        return Quaternion(
            sr * cp * cy - cr * sp * sy,
            cr * sp * cy + sr * cp * sy,
            cr * cp * sy - sr * sp * cy,
            cr * cp * cy + sr * sp * sy,
        ).normalize()

    @staticmethod
    def quaternion_to_euler(
        quaternion: Union["Quaternion", Sequence[float]],
    ) -> Tuple[float, float, float]:
        """将四元数转换为 roll、pitch、yaw。"""
        value = Quaternion.from_value(quaternion).normalize()
        sin_roll = 2.0 * (value.w * value.x + value.y * value.z)
        cos_roll = 1.0 - 2.0 * (value.x**2 + value.y**2)
        roll = math.atan2(sin_roll, cos_roll)
        sin_pitch = 2.0 * (value.w * value.y - value.z * value.x)
        pitch = math.copysign(math.pi / 2.0, sin_pitch) if abs(sin_pitch) >= 1.0 else math.asin(sin_pitch)
        sin_yaw = 2.0 * (value.w * value.z + value.x * value.y)
        cos_yaw = 1.0 - 2.0 * (value.y**2 + value.z**2)
        yaw = math.atan2(sin_yaw, cos_yaw)
        return roll, pitch, yaw

    @classmethod
    def from_value(
        cls,
        value: Union["Quaternion", Sequence[float]],
    ) -> "Quaternion":
        """从四元数或四元素序列创建对象。"""
        if isinstance(value, cls):
            return value
        if isinstance(value, (str, bytes)) or len(value) != 4:
            raise ValueError("quaternion must contain four values")
        return cls(float(value[0]), float(value[1]), float(value[2]), float(value[3]))

    def is_valid(self) -> bool:
        """检查四元数是否为有限且非零值。"""
        norm = self.x**2 + self.y**2 + self.z**2 + self.w**2
        return math.isfinite(norm) and norm > 0.0
