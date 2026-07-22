"""Traversability Sensor Adapter ?????"""

import inspect
import unittest

from traversability.adapters import (
    BaseSensorAdapter,
    DepthSensorAdapter,
    LidarSensorAdapter,
    RGBSensorAdapter,
    ThermalSensorAdapter,
)


class SensorAdapterTest(unittest.TestCase):
    """????????????????"""

    def test_adapters_are_abstract(self) -> None:
        """??????????????????"""
        for adapter_class in (
            RGBSensorAdapter,
            DepthSensorAdapter,
            LidarSensorAdapter,
            ThermalSensorAdapter,
        ):
            self.assertTrue(issubclass(adapter_class, BaseSensorAdapter))
            self.assertTrue(inspect.isabstract(adapter_class))


if __name__ == "__main__":
    unittest.main()
