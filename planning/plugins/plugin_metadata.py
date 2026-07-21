"""Planning 插件元数据模型。"""

from dataclasses import asdict, dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class PluginMetadata:
    """描述插件的通用元信息。"""

    name: str
    version: str
    author: str
    description: str

    def to_dict(self) -> Dict[str, Any]:
        """将插件元信息转换为字典。"""
        return asdict(self)


@dataclass(frozen=True)
class PlannerPluginMetadata(PluginMetadata):
    """描述全局或局部规划器插件的元信息。"""

    planner_type: str


@dataclass(frozen=True)
class ControllerPluginMetadata(PluginMetadata):
    """描述控制器插件的元信息。"""

    controller_type: str
