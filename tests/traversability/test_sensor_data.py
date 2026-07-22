"""SensorData ?????"""

import unittest

from traversability.models import SensorData


class SensorDataTest(unittest.TestCase):
    """?? SensorData ??????????"""

    def test_valid_and_copy(self) -> None:
        """??????????????????"""
        sensor_data = SensorData(
            timestamp=1.0,
            frame_id="map",
            sensor_type="rgb",
            data=[1, 2, 3],
            shape=(3,),
            encoding="uint8",
            metadata={"camera": "mock"},
        )
        copied = sensor_data.copy()
        self.assertTrue(sensor_data.is_valid())
        self.assertEqual(copied, sensor_data)
        copied.metadata["camera"] = "changed"
        self.assertNotEqual(copied.metadata, sensor_data.metadata)

    def test_invalid_without_shape(self) -> None:
        """?????????????"""
        sensor_data = SensorData(
            frame_id="map",
            sensor_type="rgb",
            data=[1, 2, 3],
        )
        self.assertFalse(sensor_data.is_valid())


if __name__ == "__main__":
    unittest.main()
