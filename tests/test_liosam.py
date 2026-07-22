"""定位模块接口。"""

import unittest

from localization import BackendConfig, BackendFactory, LocalizationManager
from localization.adapters.lidar import LioSAMAdapter
from localization.backends.lidar import LioSAMBackend
from localization.config.lidar_config import LidarConfig
from localization.models import SensorData


class LioSAMFlowTest(unittest.TestCase):
    """定位模块接口。"""

    def pointcloud_data(self) -> SensorData:
        """定位模块接口。"""
        return SensorData(
            timestamp=1.0,
            frame_id="lidar",
            sensor_type="lidar",
            data={
                "points": [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)],
                "point_time": [0.0, 0.01],
                "ring": [0, 1],
            },
        )

    def imu_data(self) -> SensorData:
        """定位模块接口。"""
        return SensorData(
            timestamp=1.01,
            frame_id="imu",
            sensor_type="imu",
            data={
                "angular_velocity": (0.0, 0.0, 0.1),
                "linear_acceleration": (0.0, 0.0, 9.8),
            },
        )

    def test_adapter_normalizes_lidar_and_imu(self) -> None:
        """定位模块接口。"""
        backend = LioSAMBackend()
        adapter = LioSAMAdapter(backend=backend)
        adapter.initialize()
        lidar_estimate = adapter.process_pointcloud(self.pointcloud_data())
        imu_estimate = adapter.process_imu(self.imu_data())
        self.assertTrue(lidar_estimate.is_valid())
        self.assertTrue(imu_estimate.is_valid())
        self.assertEqual(backend._last_pointcloud_input.data["point_time"], (0.0, 0.01))
        self.assertEqual(backend._last_pointcloud_input.data["ring"], (0, 1))
        self.assertEqual(backend._last_imu_input.data["gyro"], (0.0, 0.0, 0.1))

    def test_factory_registry_and_config(self) -> None:
        """定位模块接口。"""
        factory = BackendFactory()
        backend = factory.create_backend(BackendConfig(backend_type="LIOSAM"))
        self.assertIsInstance(backend, LioSAMBackend)
        self.assertIn("liosam", factory.get_registry().list())
        config = LidarConfig(
            lidar_topic="/points",
            imu_topic="/imu",
            lidar_frequency=10.0,
            imu_frequency=200.0,
        )
        created = factory.create_backend(config)
        self.assertIsInstance(created, LioSAMBackend)
        self.assertEqual(created._parameters["lidar_topic"], "/points")

    def test_manager_flow(self) -> None:
        """定位模块接口。"""
        backend = LioSAMBackend()
        manager = LocalizationManager(
            adapter=LioSAMAdapter(),
            backend=backend,
        )
        pose = manager.process_sensor_data(self.pointcloud_data())
        estimate = manager.get_pose_estimate()
        self.assertIsNotNone(pose)
        self.assertIsNotNone(estimate)
        self.assertEqual(estimate.source, "liosam")
        self.assertEqual(estimate.timestamp, 1.0)


if __name__ == "__main__":
    unittest.main()
