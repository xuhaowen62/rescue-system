"""Traversability 配置数据模型。"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping


@dataclass
class TraversabilityConfig:
    """保存可通过性 Provider 名称及其参数。"""

    provider_name: str = "mock"
    provider_parameters: Dict[str, Any] = field(default_factory=dict)

    def copy(self) -> "TraversabilityConfig":
        """返回配置的独立副本。"""
        return TraversabilityConfig.from_dict(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典。"""
        return asdict(self)

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "TraversabilityConfig":
        """根据字典创建配置。"""
        return cls(
            provider_name=str(data.get("provider_name", "mock")),
            provider_parameters=dict(
                data.get("provider_parameters", {})
            ),
        )