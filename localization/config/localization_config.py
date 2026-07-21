"""Localization 配置数据模型。"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping


@dataclass
class LocalizationConfig:
    """保存位姿提供器名称及其参数。"""

    provider_name: str = "mock"
    provider_parameters: Dict[str, Any] = field(default_factory=dict)

    def copy(self) -> "LocalizationConfig":
        """返回配置的独立副本。"""
        return LocalizationConfig.from_dict(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "LocalizationConfig":
        """根据字典创建配置。"""
        parameters = data.get("provider_parameters", {})
        return cls(
            provider_name=str(data.get("provider_name", "mock")),
            provider_parameters=dict(parameters),
        )