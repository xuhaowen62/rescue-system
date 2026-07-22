"""Traversability ???????????"""

import unittest

from traversability.exceptions import AnalyzerException
from traversability.plugins import AnalyzerMetadata, VersionChecker


class AnalyzerPluginTest(unittest.TestCase):
    """???????????????"""

    def test_metadata_round_trip(self) -> None:
        """?????????????????"""
        metadata = AnalyzerMetadata(
            name="rule",
            version="1.0",
            author="rescue-system",
            description="??????",
            input_type="TraversabilityInput",
            output_type="TraversabilityGrid",
            dependencies=["stdlib"],
        )
        metadata.validate()
        restored = AnalyzerMetadata.from_dict(metadata.to_dict())
        self.assertEqual(restored, metadata)
        self.assertIsNot(restored.dependencies, metadata.dependencies)

    def test_version_compatibility(self) -> None:
        """???????? Framework ??????????"""
        checker = VersionChecker("1.2")
        self.assertTrue(checker.check("1.1"))
        self.assertTrue(checker.is_compatible("1.2"))
        self.assertFalse(checker.is_compatible("1.3"))
        self.assertFalse(checker.is_compatible("2.0"))

    def test_invalid_version(self) -> None:
        """??????????? Analyzer ???"""
        with self.assertRaises(AnalyzerException):
            VersionChecker("1")


if __name__ == "__main__":
    unittest.main()
