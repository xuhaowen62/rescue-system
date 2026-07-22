"""定位坐标变换模型。"""

from dataclasses import dataclass
from typing import Sequence, Tuple, Union

from localization.models.pose import PoseState
from localization.utils.quaternion import Quaternion


@dataclass(frozen=True)
class Transform:
    """表示父坐标系到子坐标系的刚体变换。"""

    parent_frame: str
    child_frame: str
    translation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Quaternion = Quaternion.identity()

    def __post_init__(self) -> None:
        """校验坐标系和变换参数。"""
        if not str(self.parent_frame).strip() or not str(self.child_frame).strip():
            raise ValueError("frame names must not be empty")
        if len(self.translation) != 3:
            raise ValueError("translation must contain three values")
        object.__setattr__(self, "parent_frame", str(self.parent_frame).strip())
        object.__setattr__(self, "child_frame", str(self.child_frame).strip())
        object.__setattr__(
            self,
            "translation",
            tuple(float(value) for value in self.translation),
        )
        object.__setattr__(
            self,
            "rotation",
            Quaternion.from_value(self.rotation).normalize(),
        )

    def compose(self, other: "Transform") -> "Transform":
        """组合当前变换与后续变换。"""
        if not isinstance(other, Transform):
            raise TypeError("other must be Transform")
        if self.child_frame != other.parent_frame:
            raise ValueError("transform frames cannot be composed")
        offset = self.rotation.rotate_vector(other.translation)
        translation = tuple(
            self.translation[index] + offset[index] for index in range(3)
        )
        return Transform(
            parent_frame=self.parent_frame,
            child_frame=other.child_frame,
            translation=translation,
            rotation=self.rotation * other.rotation,
        )

    def inverse(self) -> "Transform":
        """返回当前变换的逆变换。"""
        rotation = self.rotation.inverse()
        translation = rotation.rotate_vector(tuple(-value for value in self.translation))
        return Transform(
            parent_frame=self.child_frame,
            child_frame=self.parent_frame,
            translation=translation,
            rotation=rotation,
        )

    def transform_pose(
        self,
        pose: Union[PoseState, "PoseEstimate"],
    ) -> Union[PoseState, "PoseEstimate"]:
        """将 PoseState 或 PoseEstimate 转换到目标坐标系。"""
        from localization.models.pose_estimate import PoseEstimate

        if isinstance(pose, PoseEstimate):
            transformed = self._transform_pose_state(pose.pose)
            result = pose.copy()
            result.pose = transformed
            result.frame_id = self.child_frame
            result.orientation_quaternion = self.rotation * pose.orientation_quaternion
            return result
        if isinstance(pose, PoseState):
            return self._transform_pose_state(pose)
        raise TypeError("pose must be PoseState or PoseEstimate")

    def _transform_pose_state(self, pose: PoseState) -> PoseState:
        """执行单个位姿状态的刚体变换。"""
        if pose.frame_id and pose.frame_id != self.parent_frame:
            raise ValueError("pose frame does not match transform parent")
        point = self.rotation.rotate_vector((pose.x, pose.y, pose.z))
        point = tuple(point[index] + self.translation[index] for index in range(3))
        orientation = self.rotation * Quaternion.euler_to_quaternion(
            pose.roll, pose.pitch, pose.yaw
        )
        roll, pitch, yaw = Quaternion.quaternion_to_euler(orientation)
        return PoseState(
            x=point[0],
            y=point[1],
            z=point[2],
            roll=roll,
            pitch=pitch,
            yaw=yaw,
            timestamp=pose.timestamp,
            frame_id=self.child_frame,
        )
