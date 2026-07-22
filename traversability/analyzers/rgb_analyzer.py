"""RGB Traversability Analyzer 空接口。"""

from traversability.analyzers.base_analyzer import BaseTraversabilityAnalyzer


class RGBTraversabilityAnalyzer(BaseTraversabilityAnalyzer):
    """为 RGB 输入预留的 Analyzer 接口，不包含视觉算法。"""

    pass
