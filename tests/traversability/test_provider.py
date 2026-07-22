"""Traversability Provider 单元测试。"""

import unittest

from traversability import (
    MockTraversabilityProvider,
    RuleBasedTraversabilityAnalyzer,
    TraversabilityInput,
    TraversabilityStatus,
)


class TraversabilityProviderTest(unittest.TestCase):
    """验证 Provider、Context 和 Analyzer 生命周期。"""

    def test_provider_flow(self) -> None:
        """Provider 应完成输入到 TraversabilityGrid 的数据流。"""
        analyzer = RuleBasedTraversabilityAnalyzer()
        provider = MockTraversabilityProvider(analyzer=analyzer)
        input_data = TraversabilityInput(
            timestamp=1.0,
            frame_id="map",
            sensor_type="occupancy",
            data=[0.0, 100.0],
            width=2,
            height=1,
            resolution=1.0,
        )
        grid = provider.analyze(input_data)
        self.assertTrue(grid.is_valid())
        self.assertEqual(provider.get_status(), TraversabilityStatus.SUCCESS)
        self.assertEqual(analyzer.get_status(), TraversabilityStatus.SUCCESS)
        context = analyzer.get_context()
        self.assertIsNotNone(context)
        self.assertEqual(context.status, TraversabilityStatus.SUCCESS)
        self.assertEqual(context.frame_id, "map")

    def test_lifecycle(self) -> None:
        """Analyzer 应支持初始化、启动、停止和重置。"""
        analyzer = RuleBasedTraversabilityAnalyzer()
        self.assertEqual(analyzer.get_status(), TraversabilityStatus.CREATED)
        analyzer.initialize()
        self.assertEqual(
            analyzer.get_status(),
            TraversabilityStatus.INITIALIZED,
        )
        analyzer.start()
        self.assertEqual(analyzer.get_status(), TraversabilityStatus.RUNNING)
        analyzer.stop()
        self.assertEqual(analyzer.get_status(), TraversabilityStatus.STOPPED)
        analyzer.reset()
        self.assertEqual(analyzer.get_status(), TraversabilityStatus.CREATED)


if __name__ == "__main__":
    unittest.main()
