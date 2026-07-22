"""SensorData ? Planning ???????????"""

import unittest

from planning.manager import PlanningManager
from planning.models import Goal, OccupancyGrid, Pose
from planning.planner import MockGlobalPlanner
from traversability.exceptions import AnalyzerException
from traversability import (
    BaseFeatureExtractor,
    BasePreprocessor,
    MockCostMapAdapter,
    RuleBasedTraversabilityAnalyzer,
    SensorData,
    TraversabilityInput,
    TraversabilityManager,
)


class MockPreprocessor(BasePreprocessor):
    """?????????????"""

    def process(self, sensor_data: SensorData) -> SensorData:
        """??????????????????"""
        return sensor_data.copy()

    def reset(self) -> None:
        """?????????"""


class MockFeatureExtractor(BaseFeatureExtractor):
    """????????????? Analyzer ???"""

    def extract(self, sensor_data: SensorData) -> TraversabilityInput:
        """?? RuleBasedAnalyzer ?????????"""
        width, height = sensor_data.shape
        resolution = float(sensor_data.metadata.get("resolution", 1.0))
        return TraversabilityInput(
            timestamp=sensor_data.timestamp,
            frame_id=sensor_data.frame_id,
            sensor_type="occupancy",
            data=list(sensor_data.data),
            width=width,
            height=height,
            resolution=resolution,
        )


class SensorPipelineTest(unittest.TestCase):
    """?? SensorData ? CostMap ? Planning ??????"""

    def test_complete_pipeline(self) -> None:
        """?????? TraversabilityGrid?CostMap ? Path?"""
        sensor_data = SensorData(
            timestamp=1.0,
            frame_id="map",
            sensor_type="occupancy",
            data=[0.0, 0.0, 100.0, 0.0],
            shape=(2, 2),
            encoding="float32",
            metadata={"resolution": 1.0},
        )
        analyzer = RuleBasedTraversabilityAnalyzer()
        grid = analyzer.analyze_sensor_data(
            sensor_data,
            MockPreprocessor(),
            MockFeatureExtractor(),
        )
        self.assertTrue(grid.is_valid())

        traversability_manager = TraversabilityManager(
            costmap_adapter=MockCostMapAdapter(),
        )
        traversability_manager.set_grid(grid)
        costmap = traversability_manager.update_costmap()
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

    def test_invalid_sensor_data(self) -> None:
        """?? SensorData ????????????"""
        analyzer = RuleBasedTraversabilityAnalyzer()
        with self.assertRaises(AnalyzerException):
            analyzer.analyze_sensor_data(
                SensorData(sensor_type="occupancy"),
                MockPreprocessor(),
                MockFeatureExtractor(),
            )


if __name__ == "__main__":
    unittest.main()
