"""Localization 第七阶段统一数据标准层测试。"""

import math
import unittest

from localization.models import CoordinateFrame, PoseEstimate, PoseState, SensorData
from localization.replay import MockReplay
from localization.utils import Quaternion, TimeSynchronizer, Timestamp, Transform


class LocalizationStage7Test(unittest.TestCase):
    """验证时间、坐标、姿态、回放和统一位姿接口。"""

    def test_timestamp_conversion_and_difference(self) -> None:
        """验证秒、毫秒、纳秒转换和时间差。"""
        timestamp = Timestamp.from_milliseconds(1500)
        self.assertAlmostEqual(timestamp.to_seconds(), 1.5)
        self.assertEqual(timestamp.to_nanoseconds(), 1_500_000_000)
        self.assertAlmostEqual(timestamp - Timestamp(1.0), 0.5)
        self.assertTrue(Timestamp(1.0) < Timestamp(2.0))

    def test_time_synchronizer(self) -> None:
        """验证 Camera、IMU、LiDAR 的轻量时间同步。"""
        synchronizer = TimeSynchronizer(tolerance=0.02)
        for sensor_type, timestamp in (("camera", 1.0), ("imu", 1.01), ("lidar", 0.995)):
            synchronizer.add_data(
                SensorData(
                    timestamp=timestamp,
                    frame_id=sensor_type,
                    sensor_type=sensor_type,
                    data={"value": sensor_type},
                )
            )
        synced = synchronizer.get_synced_data()
        self.assertIsNotNone(synced)
        self.assertEqual(set(synced), {"camera", "imu", "lidar"})

    def test_quaternion_round_trip(self) -> None:
        """验证欧拉角与四元数互转。"""
        original = (0.1, -0.2, 0.3)
        quaternion = Quaternion.euler_to_quaternion(*original)
        restored = Quaternion.quaternion_to_euler(quaternion)
        for expected, actual in zip(original, restored):
            self.assertAlmostEqual(expected, actual, places=7)
        self.assertTrue(quaternion.normalize().is_valid())

    def test_transform_compose_inverse_and_pose(self) -> None:
        """验证坐标变换组合、逆变换和位姿转换。"""
        transform = Transform(
            parent_frame=CoordinateFrame.MAP.value,
            child_frame=CoordinateFrame.ODOM.value,
            translation=(1.0, 0.0, 0.0),
        )
        pose = PoseState(x=2.0, frame_id="map", timestamp=1.0)
        transformed = transform.transform_pose(pose)
        self.assertEqual(transformed.frame_id, "odom")
        self.assertEqual(transformed.x, 3.0)
        recovered = transform.inverse().transform_pose(transformed)
        self.assertAlmostEqual(recovered.x, 2.0)

    def test_pose_estimate_supports_quaternion(self) -> None:
        """验证统一 PoseEstimate 保存四元数并保持旧属性兼容。"""
        quaternion = Quaternion.euler_to_quaternion(0.1, 0.2, 0.3)
        estimate = PoseEstimate(
            timestamp=2.0,
            frame_id="map",
            pose=PoseState(timestamp=2.0, frame_id="map"),
            orientation_quaternion=quaternion,
            source="mock",
        )
        self.assertTrue(estimate.is_valid())
        self.assertEqual(len(estimate.position), 3)
        self.assertAlmostEqual(estimate.orientation[2], 0.3)

    def test_replay(self) -> None:
        """验证 Mock 定位数据回放。"""
        replay = MockReplay()
        replay.add_data(SensorData(timestamp=1.0, sensor_type="imu", data={"x": 1}))
        self.assertTrue(replay.has_next())
        self.assertEqual(replay.read_next().timestamp, 1.0)
        self.assertIsNone(replay.read_next())
        replay.reset()
        self.assertTrue(replay.has_next())

    def test_coordinate_frame_platform_chains(self) -> None:
        """验证无人车和无人机基础坐标系链。"""
        self.assertEqual(CoordinateFrame.chain("ugv")[0], CoordinateFrame.MAP)
        self.assertIn(CoordinateFrame.CAMERA, CoordinateFrame.chain("uav"))
        self.assertEqual(
            CoordinateFrame.parent_of(CoordinateFrame.LIDAR, "ugv"),
            CoordinateFrame.BASE_LINK,
        )


if __name__ == "__main__":
    unittest.main()
