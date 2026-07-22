"""定位算法适配器数据流测试。"""

import unittest
from typing import Optional

from localization import (
    BasePlanningAdapter,
    CameraLocalizationAdapter,
    IMULocalizationAdapter,
    LocalizationManager,
    MockLocalizationAdapter,
    PoseEstimate,
    PoseState,
    SensorData,
)


class ManagerPlanningAdapter(BasePlanningAdapter):
    """验证定位模块的标准流程。"""

    def __init__(self, manager: LocalizationManager) -> None:
        """执行本测试的标准步骤。"""
        self._manager = manager

    def get_pose(self) -> Optional[PoseState]:
        """执行本测试的标准步骤。"""
        return self._manager.get_pose()


class LocalizationAdapterFlowTest(unittest.TestCase):
    """验证定位模块的标准流程。"""

    def test_pose_estimate_model(self) -> None:
        """执行本测试的标准步骤。"""
        estimate = PoseEstimate(
            timestamp=1.0,
            frame_id="map",
            pose=PoseState(x=1.0, timestamp=1.0),
            covariance=(0.1, 0.1),
            source="camera",
        )
        copied = estimate.copy()
        self.assertTrue(estimate.is_valid())
        self.assertEqual(copied, estimate)
        self.assertIsNot(copied, estimate)

    def test_camera_flow_to_manager_and_planning(self) -> None:
        """执行本测试的标准步骤。"""
        manager = LocalizationManager(
            adapter=MockLocalizationAdapter(source="camera"),
        )
        sensor_data = SensorData(
            timestamp=1.0,
            frame_id="camera",
            sensor_type="camera",
            data=[1, 2, 3],
        )
        pose = manager.process_sensor_data(sensor_data)
        estimate = manager.get_pose_estimate()
        planning_adapter = ManagerPlanningAdapter(manager)

        self.assertIsNotNone(pose)
        self.assertIsNotNone(estimate)
        self.assertTrue(estimate.is_valid())
        self.assertEqual(estimate.source, "camera")
        self.assertEqual(planning_adapter.get_pose(), pose)
        self.assertEqual(manager.get_status(), "READY")

    def test_imu_flow_and_reset(self) -> None:
        """执行本测试的标准步骤。"""
        manager = LocalizationManager(
            adapter=MockLocalizationAdapter(source="imu"),
        )
        pose = manager.process_sensor_data(
            SensorData(
                timestamp=2.0,
                frame_id="imu",
                sensor_type="imu",
                data=[0.0, 0.0, 0.0],
            )
        )
        estimate = manager.get_pose_estimate()

        self.assertEqual(pose.x, 1.0)
        self.assertEqual(estimate.source, "imu")
        manager.reset()
        self.assertIsNone(manager.get_pose())
        self.assertIsNone(manager.get_pose_estimate())
        self.assertEqual(manager.get_status(), "IDLE")

    def test_sensor_adapter_interfaces_remain_abstract(self) -> None:
        """执行本测试的标准步骤。"""
        with self.assertRaises(TypeError):
            CameraLocalizationAdapter()
        with self.assertRaises(TypeError):
            IMULocalizationAdapter()


if __name__ == "__main__":
    unittest.main()
