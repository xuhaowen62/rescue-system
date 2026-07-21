"""坐标变换工具接口预留。"""

from planning.models import Pose


def transform_pose(pose: Pose, target_frame: str) -> Pose:
    """将位姿转换到目标坐标系，具体实现后续补充。"""
    raise NotImplementedError


def convert_frame(pose: Pose, source_frame: str, target_frame: str) -> Pose:
    """在坐标系之间转换位姿，具体实现后续补充。"""
    raise NotImplementedError
