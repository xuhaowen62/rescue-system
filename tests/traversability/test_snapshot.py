"""Analyzer ???????"""

from pathlib import Path
import tempfile
import unittest

from traversability.config import AnalyzerConfigSnapshot
from traversability.exceptions import TraversabilityException


class AnalyzerSnapshotTest(unittest.TestCase):
    """?????????????"""

    def test_save_and_load(self) -> None:
        """???????????????"""
        snapshot = AnalyzerConfigSnapshot(
            analyzer_name="rule",
            enabled=True,
            parameters={"threshold": 0.5},
            timestamp=1.0,
            version="1.0",
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            snapshot.save(path)
            restored = AnalyzerConfigSnapshot.load(path)
        self.assertEqual(restored, snapshot)

    def test_invalid_snapshot(self) -> None:
        """?? Analyzer ?????????"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            with self.assertRaises(TraversabilityException):
                AnalyzerConfigSnapshot().save(path)


if __name__ == "__main__":
    unittest.main()
