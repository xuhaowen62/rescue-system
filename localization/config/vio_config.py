"""VIO 后端的配置模型。"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping


@dataclass
class VIOConfig:
    """保存 Camera、IMU 和 VIO 后端的基础配置。"""

    camera_parameters: Dict[str, Any] = field(default_factory=dict)
    imu_parameters: Dict[str, Any] = field(default_factory=dict)
    backend_type: str = "OPENVINS"
    camera_frequency: float = 0.0
    imu_frequency: float = 0.0
    backend_parameters: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """规范化配置并检查频率字段。"""
        self.backend_type = str(self.backend_type).strip().upper()
        if self.backend_type not in {"VIO", "OPENVINS"}:
            raise ValueError("backend_type must be VIO or OPENVINS")
        self.camera_parameters = dict(self.camera_parameters)
        self.imu_parameters = dict(self.imu_parameters)
        self.backend_parameters = dict(self.backend_parameters)
        self.camera_frequency = float(self.camera_frequency)
        self.imu_frequency = float(self.imu_frequency)
        if self.camera_frequency < 0 or self.imu_frequency < 0:
            raise ValueError("sensor frequency must not be negative")

    def copy(self) -> "VIOConfig":
        """返回配置的独立副本。"""
        return VIOConfig.from_dict(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典。"""
        return asdict(self)

    def to_backend_parameters(self) -> Dict[str, Any]:
        """返回传递给 Backend 的参数字典。"""
        return {
            "camera_parameters": dict(self.camera_parameters),
            "imu_parameters": dict(self.imu_parameters),
            "backend_parameters": dict(self.backend_parameters),
            "camera_frequency": self.camera_frequency,
            "imu_frequency": self.imu_frequency,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "VIOConfig":
        """根据字典创建 VIO 配置。"""
        return cls(
            camera_parameters=dict(data.get("camera_parameters", {})),
            imu_parameters=dict(data.get("imu_parameters", {})),
            backend_parameters=dict(data.get("backend_parameters", {})),
            backend_type=str(data.get("backend_type", "OPENVINS")),
            camera_frequency=float(data.get("camera_frequency", 0.0)),
            imu_frequency=float(data.get("imu_frequency", 0.0)),
        )
