"""Analyzer ?????"""

from copy import deepcopy
from dataclasses import asdict, dataclass, field
import json
import math
from pathlib import Path
from typing import Any, Dict, Mapping, Union

from traversability.exceptions import TraversabilityException


@dataclass
class AnalyzerConfigSnapshot:
    """???? Analyzer ??????????"""

    analyzer_name: str = ""
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0
    version: str = "1.0"

    def __post_init__(self) -> None:
        """????????"""
        self.analyzer_name = str(self.analyzer_name).strip()
        if isinstance(self.parameters, Mapping):
            self.parameters = dict(self.parameters)
        try:
            self.timestamp = float(self.timestamp)
        except (TypeError, ValueError):
            pass
        self.version = str(self.version).strip()

    def validate(self) -> None:
        """???????"""
        if not self.analyzer_name:
            raise TraversabilityException(
                "?????? Analyzer ??????",
                code="SNAPSHOT_INVALID",
            )
        if not self.version or not math.isfinite(self.timestamp):
            raise TraversabilityException(
                "????????????",
                code="SNAPSHOT_INVALID",
            )
        if not isinstance(self.enabled, bool):
            raise TraversabilityException(
                "???? enabled ??????",
                code="SNAPSHOT_INVALID",
            )
        if not isinstance(self.parameters, Mapping):
            raise TraversabilityException(
                "?????????????",
                code="SNAPSHOT_INVALID",
            )

    def to_dict(self) -> Dict[str, Any]:
        """?????????"""
        self.validate()
        return deepcopy(asdict(self))

    def save(self, path: Union[str, Path]) -> None:
        """???????? JSON ???"""
        try:
            target = Path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(self.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except TraversabilityException:
            raise
        except Exception as exc:
            raise TraversabilityException(
                "????????",
                code="SNAPSHOT_SAVE_FAILED",
            ) from exc

    @classmethod
    def load(cls, path: Union[str, Path]) -> "AnalyzerConfigSnapshot":
        """? JSON ?????????"""
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            if not isinstance(data, Mapping):
                raise TraversabilityException(
                    "??????? JSON ??",
                    code="SNAPSHOT_INVALID",
                )
            snapshot = cls(
                analyzer_name=data.get("analyzer_name", ""),
                enabled=data.get("enabled", True),
                parameters=deepcopy(data.get("parameters", {})),
                timestamp=data.get("timestamp", 0.0),
                version=data.get("version", "1.0"),
            )
            snapshot.validate()
            return snapshot
        except TraversabilityException:
            raise
        except Exception as exc:
            raise TraversabilityException(
                "????????",
                code="SNAPSHOT_LOAD_FAILED",
            ) from exc
