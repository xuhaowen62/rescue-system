"""定位模块统一位姿估计模型。"""

from copy import deepcopy
from dataclasses import dataclass, field
import math
from typing import Optional, Sequence, Tuple, Union

from localization.models.pose import PoseState
from localization.utils.quaternion import Quaternion


@dataclass
class PoseEstimate:
    """保存不同定位后端可共享的统一位姿结果。

    内部姿态表示使用 ``Quaternion``，同时保留 ``PoseState`` 中的欧拉角
    字段，保证既有接口兼容。四元数分量顺序为 ``x, y, z, w``。
    """

    timestamp: Optional[float] = None
    frame_id: str = "map"
    pose: PoseState = field(default_factory=PoseState)
    covariance: Optional[Tuple[float, ...]] = None
    source: str = ""
    orientation_quaternion: Optional[Quaternion] = None

    def __post_init__(self) -> None:
        """规范化字段，并同步四元数与欧拉角表示。"""
        if self.timestamp is not None:
            self.timestamp = float(self.timestamp)
        self.frame_id = str(self.frame_id).strip()
        self.source = str(self.source).strip()
        if not isinstance(self.pose, PoseState):
            raise TypeError("pose must be PoseState")
        if self.orientation_quaternion is None:
            self.orientation_quaternion = Quaternion.euler_to_quaternion(
                self.pose.roll, self.pose.pitch, self.pose.yaw
            )
        else:
            self.orientation_quaternion = Quaternion.from_value(
                self.orientation_quaternion
            ).normalize()
            self.pose.roll, self.pose.pitch, self.pose.yaw = (
                Quaternion.quaternion_to_euler(self.orientation_quaternion)
            )
        self.pose.timestamp = self.timestamp
        self.pose.frame_id = self.frame_id
        if self.covariance is not None:
            self.covariance = tuple(float(value) for value in self.covariance)

    @property
    def position(self) -> Tuple[float, float, float]:
        """返回位置分量 ``(x, y, z)``。"""
        return (self.pose.x, self.pose.y, self.pose.z)

    @property
    def orientation(self) -> Tuple[float, float, float]:
        """返回兼容旧接口的欧拉角 ``(roll, pitch, yaw)``。"""
        return (self.pose.roll, self.pose.pitch, self.pose.yaw)

    def is_valid(self) -> bool:
        """检查时间、坐标系、位姿、姿态和协方差是否合法。"""
        if self.timestamp is None or not math.isfinite(float(self.timestamp)):
            return False
        if not self.frame_id or not self.source:
            return False
        if not isinstance(self.pose, PoseState) or not self.pose.is_valid():
            return False
        if not isinstance(self.orientation_quaternion, Quaternion):
            return False
        if not self.orientation_quaternion.is_valid():
            return False
        if self.covariance is not None and not all(
            math.isfinite(float(value)) for value in self.covariance
        ):
            return False
        return True

    def copy(self) -> "PoseEstimate":
        """返回当前位姿估计的独立副本。"""
        return deepcopy(self)
