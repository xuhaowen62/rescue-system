"""Localization 第八阶段系统接口联调测试。"""

import unittest

from localization import (
    LocalizationManager,
    LocalizationPlanningAdapter,
    LocalizationStatus,
    LocalizationTraversabilityAdapter,
    MockLocalizationAdapter,
    PoseEstimate,
    SensorData,
)
from planning import Goal, MockGlobalPlanner, OccupancyGrid, PlanningManager, Pose


class LocalizationIntegrationTest(unittest.TestCase):
    """验证 Localization 到 Planning 和 Traversability 的接口链路。"""

    def _build_manager(self) -> LocalizationManager:
        """创建使用 Mock 定位适配器的管理器。"""
        manager = LocalizationManager(
            adapter=MockLocalizationAdapter(source="integration-mock")
        )
        manager.process_sensor_data(
            SensorData(
                timestamp=10.0,
                frame_id="map",
                sensor_type="camera",
                data={"mock": True},
            )
        )
        return manager

    def test_manager_unified_outputs(self) -> None:
        """验证Manager提供Pose、状态和Transform三个统一输出。"""
        manager = self._build_manager()
        pose = manager.get_current_pose()
        transform = manager.get_transform()

        self.assertIsInstance(pose, PoseEstimate)
        self.assertTrue(pose.is_valid())
        self.assertEqual(manager.get_localization_state(), "READY")
        self.assertIsNotNone(transform)
        self.assertEqual(transform.parent_frame, "map")

    def test_planning_adapter_and_planning_flow(self) -> None:
        """验证PoseEstimate转换为Planning Pose并进入Mock Planning。"""
        manager = self._build_manager()
        adapter = LocalizationPlanningAdapter(manager)
        planning_pose = adapter.get_pose()

        self.assertIsInstance(planning_pose, Pose)
        self.assertEqual(planning_pose.timestamp, 10.0)

        planning_manager = PlanningManager(global_planner=MockGlobalPlanner())
        planning_manager.set_map(
            OccupancyGrid(width=2, height=2, data=[0, 0, 0, 0])
        )
        path = planning_manager.request_plan(
            start=planning_pose,
            goal=Goal(pose=Pose(x=1.0, y=1.0, frame_id="map")),
        )
        self.assertIsNotNone(path)
        self.assertTrue(path.is_valid())

    def test_traversability_adapter_outputs(self) -> None:
        """验证Traversability可读取位置、变换和时间同步信息。"""
        manager = self._build_manager()
        adapter = LocalizationTraversabilityAdapter(manager)

        self.assertEqual(adapter.get_robot_position(), (1.0, 0.0, 0.0))
        self.assertIsNotNone(adapter.get_transform())
        self.assertEqual(
            adapter.get_time_sync_info(),
            {
                "timestamp": 10.0,
                "frame_id": "map",
                "source": "integration-mock",
            },
        )

    def test_state_query_supports_required_states(self) -> None:
        """验证统一状态查询支持初始化、运行、丢失和失败状态。"""
        manager = LocalizationManager()
        for status in (
            LocalizationStatus.INITIALIZING,
            LocalizationStatus.RUNNING,
            LocalizationStatus.LOST,
            LocalizationStatus.FAILED,
        ):
            manager.set_status(status)
            self.assertEqual(manager.get_localization_state(), status.value)


if __name__ == "__main__":
    unittest.main()
