"""Analyzer ???????"""

import unittest

from traversability import (
    RuleBasedTraversabilityAnalyzer,
    TraversabilityStatus,
)
from traversability.exceptions import TraversabilityException


class AnalyzerRecoveryTest(unittest.TestCase):
    """???? Analyzer ????????"""

    def test_failed_to_ready(self) -> None:
        """?????? FAILED??????? READY?"""
        analyzer = RuleBasedTraversabilityAnalyzer()
        with self.assertRaises(TraversabilityException):
            analyzer.analyze({"data": [], "width": 0, "height": 0})
        self.assertEqual(analyzer.get_status(), TraversabilityStatus.FAILED)
        analyzer.recover()
        self.assertEqual(analyzer.get_status(), TraversabilityStatus.READY)
        self.assertIsNone(analyzer.get_context())


if __name__ == "__main__":
    unittest.main()
