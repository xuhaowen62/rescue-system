"""Analyzer 配置数据模型。"""

from copy import deepcopy
from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Union

from traversability.exceptions import TraversabilityException


@dataclass
class AnalyzerConfig:
    """保存 Analyzer 名称、启用状态和参数。"""

    analyzer_name: str = ""
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """规范化配置字段。"""
        self.analyzer_name = str(self.analyzer_name).strip()
        if isinstance(self.parameters, Mapping):
            self.parameters = dict(self.parameters)

    def validate(self) -> None:
        """校验配置，失败时抛出统一异常。"""
        if not self.analyzer_name:
            raise TraversabilityException(
                "Analyzer 名称不能为空",
                code="CONFIG_INVALID",
            )
        if not isinstance(self.enabled, bool):
            raise TraversabilityException(
                "enabled 必须是布尔值",
                code="CONFIG_INVALID",
            )
        if not isinstance(self.parameters, Mapping):
            raise TraversabilityException(
                "parameters 必须是映射对象",
                code="CONFIG_INVALID",
            )

    def copy(self) -> "AnalyzerConfig":
        """返回配置的独立副本。"""
        return AnalyzerConfig.from_dict(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典。"""
        return deepcopy(asdict(self))

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "AnalyzerConfig":
        """根据字典创建并校验 Analyzer 配置。"""
        if not isinstance(data, Mapping):
            raise TraversabilityException(
                "配置必须是映射对象",
                code="CONFIG_INVALID",
            )
        config = cls(
            analyzer_name=data.get("analyzer_name", ""),
            enabled=data.get("enabled", True),
            parameters=deepcopy(data.get("parameters", {})),
        )
        config.validate()
        return config

    @classmethod
    def load(
        cls,
        source: Union[Mapping[str, Any], str, Path],
    ) -> "AnalyzerConfig":
        """从字典或 JSON 配置文件加载 Analyzer 配置。"""
        if isinstance(source, Mapping):
            return cls.from_dict(source)
        try:
            path = Path(source)
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            return cls.from_dict(data)
        except TraversabilityException:
            raise
        except Exception as exc:
            raise TraversabilityException(
                "Analyzer 配置加载失败",
                code="CONFIG_LOAD_FAILED",
            ) from exc

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> "AnalyzerConfig":
        """从 JSON 文件加载 Analyzer 配置。"""
        return cls.load(path)
