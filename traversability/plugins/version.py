"""Traversability Analyzer ?????????"""

import re
from typing import Optional, Tuple

from traversability.exceptions import AnalyzerException


class VersionChecker:
    """????? major/minor ???????"""

    _VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)$")

    def __init__(self, framework_version: str = "1.0") -> None:
        """?????????? Framework ???"""
        self.framework_version = self._normalize(framework_version)

    @classmethod
    def is_version(cls, version: str) -> bool:
        """??????? major.minor ???"""
        return bool(cls._VERSION_PATTERN.fullmatch(str(version).strip()))

    def is_compatible(
        self,
        analyzer_version: str,
        framework_version: Optional[str] = None,
    ) -> bool:
        """?? Analyzer ???????? Framework?"""
        analyzer = self._parse(analyzer_version)
        framework = self._parse(
            framework_version or self.framework_version
        )
        return analyzer[0] == framework[0] and analyzer[1] <= framework[1]

    def check(
        self,
        analyzer_version: str,
        framework_version: Optional[str] = None,
    ) -> bool:
        """????????????????????"""
        if not self.is_compatible(analyzer_version, framework_version):
            raise AnalyzerException(
                "Analyzer ??? Framework ???",
                code="VERSION_INCOMPATIBLE",
            )
        return True

    @classmethod
    def _normalize(cls, version: str) -> str:
        """????????????"""
        value = str(version).strip()
        if not cls.is_version(value):
            raise AnalyzerException(
                "????? major.minor ??",
                code="VERSION_INVALID",
            )
        return value

    @classmethod
    def _parse(cls, version: str) -> Tuple[int, int]:
        """????????"""
        value = cls._normalize(version)
        major, minor = value.split(".")
        return int(major), int(minor)
