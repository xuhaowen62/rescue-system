"""路径工具接口预留。"""

from planning.models import Path


def validate_path(path: Path) -> bool:
    """校验路径数据，具体实现后续补充。"""
    raise NotImplementedError


def simplify_path(path: Path) -> Path:
    """简化路径数据，具体实现后续补充。"""
    raise NotImplementedError
