"""Traversability Analyzer 注册表。"""

from typing import Dict, List, Type

from traversability.analyzers.base_analyzer import BaseTraversabilityAnalyzer
from traversability.exceptions import TraversabilityException


class AnalyzerRegistry:
    """维护 Analyzer 名称到 Analyzer 类的映射。"""

    def __init__(self) -> None:
        """创建空的 Analyzer 注册表。"""
        self._analyzers: Dict[str, Type[BaseTraversabilityAnalyzer]] = {}

    def register(
        self,
        name: str,
        analyzer_class: Type[BaseTraversabilityAnalyzer],
    ) -> None:
        """注册一个 Analyzer 类。"""
        normalized_name = str(name).strip()
        if not normalized_name:
            raise TraversabilityException(
                "Analyzer 名称不能为空",
                code="ANALYZER_NAME_INVALID",
            )
        if not isinstance(analyzer_class, type) or not issubclass(
            analyzer_class,
            BaseTraversabilityAnalyzer,
        ):
            raise TraversabilityException(
                "注册类必须继承 BaseTraversabilityAnalyzer",
                code="ANALYZER_CLASS_INVALID",
            )
        if normalized_name in self._analyzers:
            raise TraversabilityException(
                f"Analyzer 已注册: {normalized_name}",
                code="ANALYZER_ALREADY_REGISTERED",
            )
        self._analyzers[normalized_name] = analyzer_class

    def get(
        self,
        name: str,
    ) -> Type[BaseTraversabilityAnalyzer]:
        """根据名称获取 Analyzer 类。"""
        normalized_name = str(name).strip()
        try:
            return self._analyzers[normalized_name]
        except KeyError as exc:
            raise TraversabilityException(
                f"Analyzer 未注册: {normalized_name}",
                code="ANALYZER_NOT_FOUND",
            ) from exc

    def list(self) -> List[str]:
        """返回已注册 Analyzer 名称。"""
        return sorted(self._analyzers)
