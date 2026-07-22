"""定位模块接口。"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping


@dataclass
class LidarConfig:
    """定位模块接口。"""

    lidar_topic: str = ""
    lidar_frame_id: str = "lidar"
    lidar_frequency: float = 0.0
    imu_topic: str = ""
    imu_frame_id: str = "imu"
    imu_frequency: float = 0.0
    backend_type: str = "LIOSAM"
    backend_parameters: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """定位模块接口。"""
        self.lidar_topic = str(self.lidar_topic).strip()
        self.lidar_frame_id = str(self.lidar_frame_id).strip() or "lidar"
        self.imu_topic = str(self.imu_topic).strip()
        self.imu_frame_id = str(self.imu_frame_id).strip() or "imu"
        self.backend_type = str(self.backend_type).strip().upper()
        if self.backend_type not in {"LIOSAM", "LIDAR_SLAM"}:
            raise ValueError("backend_type must be LIOSAM or LIDAR_SLAM")
        self.lidar_frequency = float(self.lidar_frequency)
        self.imu_frequency = float(self.imu_frequency)
        if self.lidar_frequency < 0 or self.imu_frequency < 0:
            raise ValueError("sensor frequency must not be negative")
        self.backend_parameters = dict(self.backend_parameters)

    def copy(self) -> "LidarConfig":
        """定位模块接口。"""
        return LidarConfig.from_dict(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        """定位模块接口。"""
        return asdict(self)

    def to_backend_parameters(self) -> Dict[str, Any]:
        """定位模块接口。"""
        return {
            "lidar_topic": self.lidar_topic,
            "lidar_frame_id": self.lidar_frame_id,
            "lidar_frequency": self.lidar_frequency,
            "imu_topic": self.imu_topic,
            "imu_frame_id": self.imu_frame_id,
            "imu_frequency": self.imu_frequency,
            "backend_parameters": dict(self.backend_parameters),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "LidarConfig":
        """定位模块接口。"""
        return cls(
            lidar_topic=str(data.get("lidar_topic", data.get("topic", ""))),
            lidar_frame_id=str(data.get("lidar_frame_id", data.get("frame_id", "lidar"))),
            lidar_frequency=float(data.get("lidar_frequency", data.get("frequency", 0.0))),
            imu_topic=str(data.get("imu_topic", "")),
            imu_frame_id=str(data.get("imu_frame_id", "imu")),
            imu_frequency=float(data.get("imu_frequency", 0.0)),
            backend_type=str(data.get("backend_type", "LIOSAM")),
            backend_parameters=dict(data.get("backend_parameters", {})),
        )
