"""定位模块的统一接口和数据流处理。"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping


@dataclass
class BackendConfig:
    """定位模块的统一接口和数据流处理。"""

    backend_type: str = "MOCK"
    parameters: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """定位模块的统一接口和数据流处理。"""
        self.backend_type = str(self.backend_type).strip().upper()
        if self.backend_type not in {
            "MOCK",
            "VIO",
            "OPENVINS",
            "LIDAR_SLAM",
            "LIOSAM",
        }:
            raise ValueError(
                "backend_type must be MOCK, VIO, OPENVINS, LIDAR_SLAM or LIOSAM"
            )
        self.parameters = dict(self.parameters)

    def copy(self) -> "BackendConfig":
        """定位模块的统一接口和数据流处理。"""
        return BackendConfig.from_dict(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        """定位模块的统一接口和数据流处理。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "BackendConfig":
        """定位模块的统一接口和数据流处理。"""
        return cls(
            backend_type=str(data.get("backend_type", "MOCK")),
            parameters=dict(data.get("parameters", {})),
        )
