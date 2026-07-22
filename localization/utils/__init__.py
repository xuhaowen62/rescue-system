"""定位模块通用工具的惰性公共导出。"""

from importlib import import_module
from typing import Any

__all__ = ["Quaternion", "Timestamp", "TimeSynchronizer", "Transform"]


def __getattr__(name: str) -> Any:
    """按需加载工具，避免模型初始化时产生循环导入。"""
    modules = {
        "Quaternion": "localization.utils.quaternion",
        "Timestamp": "localization.utils.time.timestamp",
        "TimeSynchronizer": "localization.utils.time.synchronizer",
        "Transform": "localization.utils.transform.transform",
    }
    if name not in modules:
        raise AttributeError(name)
    return getattr(import_module(modules[name]), name)
