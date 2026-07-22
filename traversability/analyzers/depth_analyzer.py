"""Depth Traversability Analyzer 空接口。"""

from traversability.analyzers.base_analyzer import BaseTraversabilityAnalyzer


class DepthTraversabilityAnalyzer(BaseTraversabilityAnalyzer):
    """为深度输入预留的 Analyzer 接口，不包含深度算法。"""

    pass
