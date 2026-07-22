"""Traversability ???????"""

import math
import unittest

from traversability.exceptions import TraversabilityException
from traversability.models import TraversabilityInput


class TraversabilityBoundaryTest(unittest.TestCase):
    """????????????? frame_id ???"""

    def test_empty_input(self) -> None:
        """????????????"""
        input_data = TraversabilityInput()
        self.assertFalse(input_data.is_valid())
        with self.assertRaises(TraversabilityException):
            input_data.validate()

    def test_size_error(self) -> None:
        """???????????????"""
        input_data = TraversabilityInput(
            data=[0.0],
            width=2,
            height=1,
            resolution=1.0,
        )
        self.assertFalse(input_data.is_valid())

    def test_timestamp_error(self) -> None:
        """?????????????"""
        input_data = TraversabilityInput(
            timestamp=math.nan,
            data=[0.0],
            width=1,
            height=1,
            resolution=1.0,
        )
        self.assertFalse(input_data.is_valid())

    def test_frame_id_error(self) -> None:
        """? frame_id ???????"""
        input_data = TraversabilityInput(
            frame_id="",
            data=[0.0],
            width=1,
            height=1,
            resolution=1.0,
        )
        self.assertFalse(input_data.is_valid())


if __name__ == "__main__":
    unittest.main()
