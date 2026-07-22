"""AnalyzerFactory 单元测试。"""

import json
from pathlib import Path
import tempfile
import unittest

from traversability.analyzers import (
    AnalyzerRegistry,
    RuleBasedTraversabilityAnalyzer,
)
from traversability.config import AnalyzerConfig
from traversability.exceptions import TraversabilityException
from traversability.factory import AnalyzerFactory


class AnalyzerFactoryTest(unittest.TestCase):
    """验证配置加载和 Analyzer 创建流程。"""

    def setUp(self) -> None:
        """创建测试用注册表和工厂。"""
        self.registry = AnalyzerRegistry()
        self.registry.register("rule", RuleBasedTraversabilityAnalyzer)
        self.factory = AnalyzerFactory(self.registry)

    def test_create_analyzer(self) -> None:
        """Factory 应根据 Registry 和 Config 创建正确实例。"""
        config = AnalyzerConfig(
            analyzer_name="rule",
            parameters={"occupancy_risk_threshold": 20.0},
        )
        analyzer = self.factory.create_analyzer(config)
        self.assertIsInstance(analyzer, RuleBasedTraversabilityAnalyzer)

    def test_load_config(self) -> None:
        """Factory 应能够使用文件加载的配置创建 Analyzer。"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "analyzer.json"
            path.write_text(
                json.dumps({
                    "analyzer_name": "rule",
                    "enabled": True,
                    "parameters": {},
                }),
                encoding="utf-8",
            )
            config = AnalyzerConfig.load(path)
        self.assertEqual(config.analyzer_name, "rule")
        self.assertIsInstance(self.factory.create_analyzer(config),
                              RuleBasedTraversabilityAnalyzer)

    def test_invalid_config(self) -> None:
        """配置错误时应抛出统一异常。"""
        with self.assertRaises(TraversabilityException):
            AnalyzerConfig.from_dict({"enabled": True})


if __name__ == "__main__":
    unittest.main()
