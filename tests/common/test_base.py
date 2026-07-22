"""Traversability Analyzer ???????"""

import unittest

from traversability.models import TraversabilityGrid, TraversabilityInput


class AnalyzerTestBase(unittest.TestCase):
    """?? Analyzer ????????????"""

    def create_valid_input(self) -> TraversabilityInput:
        """?????????????????"""
        return TraversabilityInput(
            timestamp=1.0,
            frame_id="map",
            sensor_type="occupancy",
            data=[0.0],
            width=1,
            height=1,
            resolution=1.0,
        )

    def assert_valid_input(self, input_data: TraversabilityInput) -> None:
        """?????????"""
        self.assertIsInstance(input_data, TraversabilityInput)
        self.assertTrue(input_data.is_valid())

    def assert_valid_grid(self, grid: TraversabilityGrid) -> None:
        """?? Analyzer ???????"""
        self.assertIsInstance(grid, TraversabilityGrid)
        self.assertTrue(grid.is_valid())
