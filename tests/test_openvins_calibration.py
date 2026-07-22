"""OpenVINS 输入校准层的 Mock 测试。"""

import unittest
from pathlib import Path

from localization.adapters.vio import OpenVINSAdapter
from localization.backends.vio import OpenVINSBackend
from localization.config.vio_config import VIOConfig
from localization.models import SensorData


class OpenVINSCalibrationTest(unittest.TestCase):
    """验证数据转换和接口边界，不验证真实 VIO 算法。"""

    def setUp(self) -> None:
        """创建已初始化的适配器和后端。"""
        self.backend = OpenVINSBackend()
        self.adapter = OpenVINSAdapter(backend=self.backend)
        self.adapter.initialize()

    def test_camera_payload_matches_camera_data_shape(self) -> None:
        """验证图像输入被转换为相机编号和图像列表。"""
        estimate = self.adapter.process_image(
            SensorData(
                timestamp=1.0,
                frame_id="camera",
                sensor_type="camera",
                data={"image": "mock-image", "sensor_id": 0},
            )
        )
        self.assertTrue(estimate.is_valid())
        camera_input = self.backend._last_camera_input
        self.assertIsNotNone(camera_input)
        self.assertEqual(camera_input.data["sensor_ids"], (0,))
        self.assertEqual(camera_input.data["images"], ("mock-image",))

    def test_imu_payload_matches_imu_data_shape(self) -> None:
        """验证 IMU 输入被转换为 wm 和 am 三轴数据。"""
        self.adapter.process_imu(
            SensorData(
                timestamp=1.01,
                frame_id="imu",
                sensor_type="imu",
                data={
                    "angular_velocity": (1.0, 2.0, 3.0),
                    "linear_acceleration": (4.0, 5.0, 6.0),
                },
            )
        )
        imu_input = self.backend._last_imu_input
        self.assertIsNotNone(imu_input)
        self.assertEqual(imu_input.data["wm"], (1.0, 2.0, 3.0))
        self.assertEqual(imu_input.data["am"], (4.0, 5.0, 6.0))

    def test_invalid_imu_vector_is_rejected(self) -> None:
        """验证非三轴 IMU 输入被拒绝。"""
        with self.assertRaises(Exception):
            self.adapter.process_imu(
                SensorData(
                    timestamp=1.0,
                    frame_id="imu",
                    sensor_type="imu",
                    data={"gyro": (1.0, 2.0), "accel": (0.0, 0.0, 0.0)},
                )
            )

    def test_pose_and_config_contract(self) -> None:
        """验证统一 PoseEstimate 字段和后端参数配置。"""
        estimate = self.adapter.process_sensor_data(
            SensorData(
                timestamp=2.0,
                frame_id="camera",
                sensor_type="camera",
                data="mock-image",
            )
        )
        self.assertEqual(estimate.position, (0.0, 0.0, 0.0))
        self.assertEqual(estimate.orientation, (0.0, 0.0, 0.0))
        config = VIOConfig(backend_parameters={"max_clones": 11})
        self.assertEqual(
            config.to_backend_parameters()["backend_parameters"]["max_clones"],
            11,
        )

    def test_reference_document_exists(self) -> None:
        """验证 OpenVINS 参考说明文档已加入项目。"""
        document = (
            Path(__file__).parents[1]
            / "docs"
            / "localization"
            / "openvins_reference.md"
        )
        self.assertTrue(document.is_file())


if __name__ == "__main__":
    unittest.main()
