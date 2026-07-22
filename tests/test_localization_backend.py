"""定位模块的统一接口和数据流处理。"""

import unittest
from typing import Optional

from localization import (
    BackendFactory,
    BasePlanningAdapter,
    LocalizationManager,
    MockLocalizationAdapter,
    PoseState,
    SensorData,
)


class ManagerPlanningAdapter(BasePlanningAdapter):
    """定位模块的统一接口和数据流处理。"""

    def __init__(self, manager: LocalizationManager) -> None:
        """定位模块的统一接口和数据流处理。"""
        self._manager = manager

    def get_pose(self) -> Optional[PoseState]:
        """定位模块的统一接口和数据流处理。"""
        return self._manager.get_pose()


class LocalizationBackendFlowTest(unittest.TestCase):
    """定位模块的统一接口和数据流处理。"""

    def test_factory_and_registry_create_mock_backend(self) -> None:
        """定位模块的统一接口和数据流处理。"""
        factory = BackendFactory()
        backend = factory.create_backend(
            {
                "backend_name": "mock",
                "parameters": {"source": "factory-mock"},
            }
        )
        self.assertIn("mock", factory.get_registry().list())
        self.assertEqual(backend.__class__.__name__, "MockLocalizationBackend")

    def test_camera_adapter_backend_manager_flow(self) -> None:
        """定位模块的统一接口和数据流处理。"""
        manager = LocalizationManager(
            adapter=MockLocalizationAdapter(source="camera"),
            backend=BackendFactory().create_backend(
                "mock",
                {"source": "mock-backend"},
            ),
        )
        pose = manager.process_sensor_data(
            SensorData(
                timestamp=1.0,
                frame_id="camera",
                sensor_type="camera",
                data=[1, 2, 3],
            )
        )
        estimate = manager.get_pose_estimate()
        planning_adapter = ManagerPlanningAdapter(manager)

        self.assertIsNotNone(pose)
        self.assertIsNotNone(estimate)
        self.assertTrue(estimate.is_valid())
        self.assertEqual(estimate.source, "mock-backend")
        self.assertEqual(planning_adapter.get_pose(), pose)
        self.assertEqual(manager.get_status(), "READY")

    def test_imu_adapter_backend_flow_and_reset(self) -> None:
        """定位模块的统一接口和数据流处理。"""
        manager = LocalizationManager(
            adapter=MockLocalizationAdapter(source="imu"),
            backend=BackendFactory().create_backend("mock"),
        )
        pose = manager.process_sensor_data(
            SensorData(
                timestamp=2.0,
                frame_id="imu",
                sensor_type="imu",
                data=[0.0, 0.0, 0.0],
            )
        )

        self.assertEqual(pose.x, 1.0)
        self.assertEqual(manager.get_pose_estimate().source, "mock-backend")
        manager.reset()
        self.assertIsNone(manager.get_pose())
        self.assertIsNone(manager.get_pose_estimate())
        self.assertEqual(manager.get_status(), "IDLE")


if __name__ == "__main__":
    unittest.main()
