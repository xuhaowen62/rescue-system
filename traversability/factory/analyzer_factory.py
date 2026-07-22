"""Analyzer 工厂。"""

from typing import Any

from traversability.analyzers.base_analyzer import BaseTraversabilityAnalyzer
from traversability.analyzers.registry import AnalyzerRegistry
from traversability.config import AnalyzerConfig
from traversability.exceptions import TraversabilityException


class AnalyzerFactory:
    """根据配置和注册表创建 Analyzer 实例。"""

    def __init__(self, registry: AnalyzerRegistry) -> None:
        """创建使用指定注册表的工厂。"""
        if not isinstance(registry, AnalyzerRegistry):
            raise TypeError("registry 必须是 AnalyzerRegistry 实例")
        self._registry = registry

    def create_analyzer(
        self,
        config: AnalyzerConfig,
        **overrides: Any,
    ) -> BaseTraversabilityAnalyzer:
        """根据配置创建 Analyzer，不依赖任何具体算法。"""
        if not isinstance(config, AnalyzerConfig):
            raise TypeError("config 必须是 AnalyzerConfig 实例")
        if not config.enabled:
            raise TraversabilityException(
                "Analyzer 未启用",
                code="ANALYZER_DISABLED",
            )
        analyzer_class = self._registry.get(config.analyzer_name)
        parameters = dict(config.parameters)
        parameters.update(overrides)
        try:
            analyzer = analyzer_class(**parameters)
        except Exception as exc:
            raise TraversabilityException(
                "Analyzer 创建失败",
                code="ANALYZER_CREATE_FAILED",
            ) from exc
        return analyzer

