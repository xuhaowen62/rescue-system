"""AnalyzerRegistry 单元测试。"""

import unittest

from traversability.analyzers import (
    AnalyzerRegistry,
    RuleBasedTraversabilityAnalyzer,
)
from traversability.exceptions import TraversabilityException


class AnalyzerRegistryTest(unittest.TestCase):
    """验证 Analyzer 注册、查询和异常行为。"""

    def test_register_and_get(self) -> None:
        """注册后应能查询 Analyzer 类。"""
        registry = AnalyzerRegistry()
        registry.register("rule", RuleBasedTraversabilityAnalyzer)
        self.assertIs(
            registry.get("rule"),
            RuleBasedTraversabilityAnalyzer,
        )
        self.assertEqual(registry.list(), ["rule"])

    def test_duplicate_register(self) -> None:
        """重复注册名称时应抛出统一异常。"""
        registry = AnalyzerRegistry()
        registry.register("rule", RuleBasedTraversabilityAnalyzer)
        with self.assertRaises(TraversabilityException):
            registry.register("rule", RuleBasedTraversabilityAnalyzer)

    def test_unknown_analyzer(self) -> None:
        """查询未注册 Analyzer 时应抛出统一异常。"""
        with self.assertRaises(TraversabilityException):
            AnalyzerRegistry().get("missing")


if __name__ == "__main__":
    unittest.main()
