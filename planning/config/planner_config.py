"""Planning 规划器配置模型。"""

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping, Optional


@dataclass
class PlannerConfig:
    """保存全局规划器、局部规划器和控制器名称及参数。"""

    planner_name: str = ""
    controller_name: str = ""
    planner_parameters: Dict[str, Any] = field(default_factory=dict)
    controller_parameters: Dict[str, Any] = field(default_factory=dict)
    local_planner_name: str = ""

    def copy(self) -> "PlannerConfig":
        """返回配置的独立副本。"""
        return deepcopy(self)

    def to_dict(self) -> Dict[str, Any]:
        """将规划配置转换为字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PlannerConfig":
        """从字典创建规划配置。"""
        return cls(
            planner_name=str(data.get("planner_name", "")),
            controller_name=str(data.get("controller_name", "")),
            planner_parameters=dict(data.get("planner_parameters", {})),
            controller_parameters=dict(
                data.get("controller_parameters", {})
            ),
            local_planner_name=str(data.get("local_planner_name", "")),
        )
