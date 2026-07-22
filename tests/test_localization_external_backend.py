"""定位模块的统一接口和数据流处理。"""

import unittest

from localization import (
    BackendConfig,
    BackendFactory,
    ExternalLocalizationBackend,
    LidarSLAMBackend,
    MockLocalizationBackend,
    SensorData,
    VIOBackend,
)


class ExternalBackendArchitectureTest(unittest.TestCase):
    """定位模块的统一接口和数据流处理。"""

    def test_backend_config(self) -> None:
        """定位模块的统一接口和数据流处理。"""
        config = BackendConfig.from_dict(
            {
                "backend_type": "lidar_slam",
                "parameters": {"frame": "map"},
            }
        )
        self.assertEqual(config.backend_type, "LIDAR_SLAM")
        self.assertEqual(config.parameters["frame"], "map")
        self.assertEqual(config.copy(), config)

    def test_factory_creates_all_backend_interfaces(self) -> None:
        """定位模块的统一接口和数据流处理。"""
        factory = BackendFactory()
        mock_backend = factory.create_backend("MOCK")
        vio_backend = factory.create_backend(
            BackendConfig(backend_type="VIO")
        )
        lidar_backend = factory.create_backend(
            BackendConfig(backend_type="LIDAR_SLAM")
        )

        self.assertIsInstance(mock_backend, MockLocalizationBackend)
        self.assertIsInstance(vio_backend, VIOBackend)
        self.assertIsInstance(lidar_backend, LidarSLAMBackend)
        self.assertIsInstance(vio_backend, ExternalLocalizationBackend)
        self.assertIsInstance(lidar_backend, ExternalLocalizationBackend)

    def test_vio_interface_lifecycle(self) -> None:
        """定位模块的统一接口和数据流处理。"""
        backend = VIOBackend()
        sensor_data = SensorData(
            timestamp=1.0,
            frame_id="camera",
            sensor_type="camera",
            data=[1, 2, 3],
        )
        backend.initialize()
        self.assertIsNone(backend.process_image(sensor_data))
        self.assertIsNone(backend.process_imu(sensor_data))
        self.assertIsNone(backend.get_pose())
        backend.shutdown()

    def test_lidar_slam_interface_lifecycle(self) -> None:
        """定位模块的统一接口和数据流处理。"""
        backend = LidarSLAMBackend()
        sensor_data = SensorData(
            timestamp=1.0,
            frame_id="lidar",
            sensor_type="lidar",
            data=[0.0, 1.0, 2.0],
        )
        backend.initialize()
        self.assertIsNone(backend.process_pointcloud(sensor_data))
        self.assertIsNone(backend.process_imu(sensor_data))
        self.assertIsNone(backend.get_pose())
        backend.shutdown()


if __name__ == "__main__":
    unittest.main()
