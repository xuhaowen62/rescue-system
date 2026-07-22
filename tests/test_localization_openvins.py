"""OpenVINS 适配层的 Mock 流程测试。"""

import unittest

from localization import BackendConfig, BackendFactory, LocalizationManager
from localization.adapters.vio import OpenVINSAdapter
from localization.backends.vio import OpenVINSBackend
from localization.core import LocalizationStatus
from localization.models import SensorData


class OpenVINSFlowTest(unittest.TestCase):
    """验证 OpenVINS 接入层的数据流，不验证真实算法。"""

    def camera_data(self) -> SensorData:
        """创建 Mock Camera 数据。"""
        return SensorData(
            timestamp=1.0,
            frame_id="camera",
            sensor_type="camera",
            data=[1, 2, 3],
        )

    def imu_data(self) -> SensorData:
        """创建 Mock IMU 数据。"""
        return SensorData(
            timestamp=1.01,
            frame_id="imu",
            sensor_type="imu",
            data=[0.0, 0.0, 0.0],
        )

    def test_adapter_and_backend_interfaces(self) -> None:
        """验证 Camera、IMU 可进入统一 PoseEstimate 接口。"""
        backend = OpenVINSBackend()
        adapter = OpenVINSAdapter()
        adapter.initialize()
        backend.initialize()

        camera_estimate = adapter.process_image(self.camera_data())
        imu_estimate = adapter.process_imu(self.imu_data())
        backend_estimate = backend.process_image(self.camera_data())

        self.assertTrue(camera_estimate.is_valid())
        self.assertTrue(imu_estimate.is_valid())
        self.assertTrue(backend_estimate.is_valid())
        self.assertEqual(backend.get_pose(), backend_estimate)

    def test_factory_registry_and_manager_flow(self) -> None:
        """验证 Factory、Registry、Adapter、Backend、Manager 的完整流程。"""
        factory = BackendFactory()
        backend = factory.create_backend(BackendConfig(backend_type="OPENVINS"))
        manager = LocalizationManager(
            adapter=OpenVINSAdapter(),
            backend=backend,
        )

        pose = manager.process_sensor_data(self.camera_data())
        self.assertIsNotNone(pose)
        self.assertIsNotNone(manager.get_pose_estimate())
        self.assertEqual(manager.get_pose_estimate().source, "openvins")
        self.assertIn("openvins", factory.get_registry().list())
        self.assertEqual(manager.get_status(), LocalizationStatus.READY.value)

    def test_invalid_sensor_data_fails_without_algorithm(self) -> None:
        """验证无效传感器输入会被统一拒绝。"""
        adapter = OpenVINSAdapter()
        adapter.initialize()
        with self.assertRaises(Exception):
            adapter.process_sensor_data(SensorData(sensor_type="camera"))


if __name__ == "__main__":
    unittest.main()
