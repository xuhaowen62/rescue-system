"""CostMap Adapter 单元测试。"""

import unittest

from traversability import MockCostMapAdapter, TraversabilityGrid


class CostMapAdapterTest(unittest.TestCase):
    """验证 TraversabilityGrid 到 CostMap 的转换。"""

    def test_grid_to_costmap(self) -> None:
        """可通过性值应转换为对应 CostMap 数值。"""
        grid = TraversabilityGrid(
            width=3,
            height=1,
            resolution=1.0,
            data=[1.0, 0.5, 0.0],
        )
        costmap = MockCostMapAdapter().convert_to_costmap(grid)
        self.assertTrue(costmap.is_valid())
        self.assertEqual(costmap.data, [0.0, 50.0, 100.0])


if __name__ == "__main__":
    unittest.main()
