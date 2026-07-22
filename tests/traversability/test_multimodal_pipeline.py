"""??????? Traversability ?????"""

import unittest

from planning.manager import PlanningManager
from planning.models import Goal, OccupancyGrid, Pose
from planning.planner import MockGlobalPlanner
from traversability import (
    DepthEncoder,
    FeatureRepresentation,
    LiDAREncoder,
    MockCostMapAdapter,
    MultiModalPipeline,
    RGBEncoder,
    RulePredictor,
    SimpleFusion,
    ThermalEncoder,
    SensorData,
    TraversabilityManager,
)


class MockRGBEncoder(RGBEncoder):
    """???? RGB ????? Encoder?"""

    def encode(self, sensor_data: SensorData) -> FeatureRepresentation:
        """??????? RGB ???"""
        return FeatureRepresentation(
            sensor_type="rgb",
            timestamp=sensor_data.timestamp,
            frame_id=sensor_data.frame_id,
            feature_data=[1.0, 0.8, 0.4, 0.0],
            shape=(2, 2),
            metadata={"resolution": 1.0},
        )

    def reset(self) -> None:
        """???? RGB Encoder?"""


class MockDepthEncoder(DepthEncoder):
    """???? Depth ????? Encoder?"""

    def encode(self, sensor_data: SensorData) -> FeatureRepresentation:
        """????????????"""
        return FeatureRepresentation(
            sensor_type="depth",
            timestamp=sensor_data.timestamp,
            frame_id=sensor_data.frame_id,
            feature_data=[1.0, 0.6, 0.2, 0.8],
            shape=(2, 2),
            metadata={"resolution": 1.0},
        )

    def reset(self) -> None:
        """???? Depth Encoder?"""


class MockThermalEncoder(ThermalEncoder):
    """???????????? Encoder?"""

    def encode(self, sensor_data: SensorData) -> FeatureRepresentation:
        """?????????????"""
        return FeatureRepresentation(
            sensor_type="thermal",
            timestamp=sensor_data.timestamp,
            frame_id=sensor_data.frame_id,
            feature_data=[0.8, 0.4, 1.0, 0.2],
            shape=(2, 2),
            metadata={"resolution": 1.0},
        )

    def reset(self) -> None:
        """???? Thermal Encoder?"""


class MultimodalPipelineTest(unittest.TestCase):
    """???????? Planning Path ??????"""

    def setUp(self) -> None:
        """?????????"""
        self.pipeline = MultiModalPipeline(
            encoders={
                "rgb": MockRGBEncoder(),
                "depth": MockDepthEncoder(),
                "thermal": MockThermalEncoder(),
            },
            fusion=SimpleFusion(),
            predictor=RulePredictor(),
        )

    def test_feature_representation(self) -> None:
        """FeatureRepresentation ????????????"""
        feature = FeatureRepresentation(
            sensor_type="rgb",
            feature_data=[0.1, 0.2],
            shape=(2,),
        )
        copied = feature.copy()
        self.assertTrue(feature.is_valid())
        self.assertEqual(copied, feature)

    def test_complete_flow(self) -> None:
        """RGB?Depth?Thermal ???????????????"""
        sensor_data = [
            SensorData(
                timestamp=1.0,
                frame_id="map",
                sensor_type="rgb",
                data=[1, 2, 3, 4],
                shape=(2, 2),
                encoding="mock",
            ),
            SensorData(
                timestamp=1.0,
                frame_id="map",
                sensor_type="depth",
                data=[1, 2, 3, 4],
                shape=(2, 2),
                encoding="mock",
            ),
            SensorData(
                timestamp=1.0,
                frame_id="map",
                sensor_type="thermal",
                data=[1, 2, 3, 4],
                shape=(2, 2),
                encoding="mock",
            ),
        ]
        grid = self.pipeline.run(sensor_data)
        self.assertTrue(grid.is_valid())
        self.assertEqual((grid.width, grid.height), (2, 2))

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

    def test_unknown_modality(self) -> None:
        """?????????????"""
        sensor_data = SensorData(
            timestamp=1.0,
            frame_id="map",
            sensor_type="unknown",
            data=[1],
            shape=(1,),
            encoding="mock",
        )
        with self.assertRaises(ValueError):
            self.pipeline.run([sensor_data])

    def test_reset(self) -> None:
        """???????????? Encoder?"""
        self.pipeline.reset()


if __name__ == "__main__":
    unittest.main()
