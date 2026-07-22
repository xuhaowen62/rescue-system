"""Traversability Analyzer ????????"""

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping

from traversability.exceptions import AnalyzerException
from traversability.plugins.version import VersionChecker


@dataclass
class AnalyzerMetadata:
    """?? Analyzer ??????????????????"""

    name: str = ""
    version: str = "1.0"
    author: str = ""
    description: str = ""
    input_type: str = ""
    output_type: str = "TraversabilityGrid"
    dependencies: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """?????????"""
        self.name = str(self.name).strip()
        self.version = str(self.version).strip()
        self.author = str(self.author).strip()
        self.description = str(self.description).strip()
        self.input_type = str(self.input_type).strip()
        self.output_type = str(self.output_type).strip()
        self.dependencies = [str(item).strip() for item in self.dependencies]

    def validate(self) -> None:
        """????????????????"""
        if not self.name:
            raise AnalyzerException(
                "Analyzer ????????",
                code="METADATA_NAME_INVALID",
            )
        if not VersionChecker.is_version(self.version):
            raise AnalyzerException(
                "Analyzer ??????? major.minor ??",
                code="METADATA_VERSION_INVALID",
            )
        if not self.input_type or not self.output_type:
            raise AnalyzerException(
                "Analyzer ????????????",
                code="METADATA_TYPE_INVALID",
            )
        if any(not dependency for dependency in self.dependencies):
            raise AnalyzerException(
                "Analyzer ??????????",
                code="METADATA_DEPENDENCY_INVALID",
            )

    def copy(self) -> "AnalyzerMetadata":
        """???????????"""
        return AnalyzerMetadata.from_dict(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        """??????????????"""
        return deepcopy(asdict(self))

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "AnalyzerMetadata":
        """???????????????"""
        if not isinstance(data, Mapping):
            raise AnalyzerException(
                "????????????",
                code="METADATA_INVALID",
            )
        metadata = cls(
            name=data.get("name", ""),
            version=data.get("version", "1.0"),
            author=data.get("author", ""),
            description=data.get("description", ""),
            input_type=data.get("input_type", ""),
            output_type=data.get("output_type", "TraversabilityGrid"),
            dependencies=deepcopy(data.get("dependencies", [])),
        )
        metadata.validate()
        return metadata

