"""Traversability 到 Planning 的完整集成测试。"""

import unittest

from planning.manager import PlanningManager
from planning.models import Goal, OccupancyGrid, Pose
from planning.planner import MockGlobalPlanner
from traversability import (
    AnalyzerConfig,
    AnalyzerFactory,
    AnalyzerRegistry,
    MockCostMapAdapter,
    MockTraversabilityProvider,
    RuleBasedTraversabilityAnalyzer,
    TraversabilityInput,
    TraversabilityManager,
)


class TraversabilityIntegrationTest(unittest.TestCase):
    """验证从输入到 Planning Path 的跨模块数据流。"""

    def test_complete_flow(self) -> None:
        """应完成 Input 到 CostMap 再到 Mock Path 的流程。"""
        registry = AnalyzerRegistry()
        registry.register("rule", RuleBasedTraversabilityAnalyzer)
        analyzer = AnalyzerFactory(registry).create_analyzer(
            AnalyzerConfig("rule")
        )
        provider = MockTraversabilityProvider(analyzer=analyzer)
        traversability_manager = TraversabilityManager(
            provider=provider,
            costmap_adapter=MockCostMapAdapter(),
        )
        input_data = TraversabilityInput(
            timestamp=1.0,
            frame_id="map",
            sensor_type="occupancy",
            data=[0.0, 0.0, 100.0, 0.0],
            width=2,
            height=2,
            resolution=1.0,
        )
        grid = traversability_manager.update_grid(input_data)
        costmap = traversability_manager.update_costmap()
        self.assertIsNotNone(grid)
        self.assertIsNotNone(costmap)

        planning_manager = PlanningManager(
            global_planner=MockGlobalPlanner(),
        )
        planning_manager.set_map(
            OccupancyGrid(
                width=2,
                height=2,
                resolution=1.0,
                data=[0, 0, 100, 0],
            )
        )
        planning_manager.set_costmap(costmap)
        path = planning_manager.request_plan(
            Pose(x=0.0, y=0.0),
            Goal(target_id="target", pose=Pose(x=1.0, y=1.0)),
        )
        self.assertIsNotNone(path)
        self.assertTrue(path.is_valid())


if __name__ == "__main__":
    unittest.main()
