"""TraversabilityInput 单元测试。"""

import unittest

from traversability.exceptions import TraversabilityException
from traversability.models import TraversabilityInput


class TraversabilityInputTest(unittest.TestCase):
    """验证统一输入模型的字段和校验行为。"""

    def test_valid_input(self) -> None:
        """有效输入应通过校验。"""
        input_data = TraversabilityInput(
            timestamp=1.0,
            frame_id="map",
            sensor_type="occupancy",
            data=[0.0, 50.0, 100.0, 25.0],
            width=2,
            height=2,
            resolution=0.5,
        )
        self.assertTrue(input_data.is_valid())
        input_data.validate()

    def test_invalid_size(self) -> None:
        """数据长度不一致时应抛出统一异常。"""
        input_data = TraversabilityInput(
            frame_id="map",
            sensor_type="occupancy",
            data=[0.0],
            width=2,
            height=1,
            resolution=1.0,
        )
        self.assertFalse(input_data.is_valid())
        with self.assertRaises(TraversabilityException):
            input_data.validate()

    def test_reset(self) -> None:
        """重置后输入应回到未初始化状态。"""
        input_data = TraversabilityInput(
            frame_id="map",
            sensor_type="occupancy",
            data=[0.0],
            width=1,
            height=1,
            resolution=1.0,
        )
        input_data.reset()
        self.assertFalse(input_data.is_valid())
        self.assertEqual(input_data.data, [])


if __name__ == "__main__":
    unittest.main()
