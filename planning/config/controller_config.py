"""Planning 控制器配置模型。"""

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping


@dataclass
class ControllerConfig:
    """保存控制器名称和参数。"""

    controller_name: str = ""
    controller_parameters: Dict[str, Any] = field(default_factory=dict)

    def copy(self) -> "ControllerConfig":
        """返回配置的独立副本。"""
        return deepcopy(self)

    def to_dict(self) -> Dict[str, Any]:
        """将控制器配置转换为字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ControllerConfig":
        """从字典创建控制器配置。"""
        return cls(
            controller_name=str(data.get("controller_name", "")),
            controller_parameters=dict(
                data.get("controller_parameters", {})
            ),
        )
