"""几何工具接口预留。"""

from planning.models import Pose


def distance(first: Pose, second: Pose) -> float:
    """计算两个位姿之间的距离，具体实现后续补充。"""
    raise NotImplementedError


def normalize_angle(angle: float) -> float:
    """将角度归一化到标准范围，具体实现后续补充。"""
    raise NotImplementedError
