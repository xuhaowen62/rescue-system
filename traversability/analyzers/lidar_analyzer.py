"""LiDAR Traversability Analyzer 空接口。"""

from traversability.analyzers.base_analyzer import BaseTraversabilityAnalyzer


class LidarTraversabilityAnalyzer(BaseTraversabilityAnalyzer):
    """为 LiDAR 输入预留的 Analyzer 接口，不包含点云算法。"""

    pass
