"""定位模块的统一接口和数据流处理。"""

from typing import Any, Mapping, Optional

from localization.backends import (
    LioSAMBackend,
    LidarSLAMBackend,
    MockLocalizationBackend,
    OpenVINSBackend,
    VIOBackend,
)
from localization.backends.base_backend import BaseLocalizationBackend
from localization.exceptions import LocalizationException
from localization.registry import BackendRegistry


class BackendFactory:
    """定位模块的统一接口和数据流处理。"""

    def __init__(self, registry: Optional[BackendRegistry] = None) -> None:
        """定位模块的统一接口和数据流处理。"""
        self._registry = registry or BackendRegistry()
        defaults = {
            "mock": MockLocalizationBackend,
            "vio": VIOBackend,
            "lidar_slam": LidarSLAMBackend,
            "openvins": OpenVINSBackend,
            "liosam": LioSAMBackend,
        }
        for name, backend_type in defaults.items():
            if name not in self._registry.list():
                self._registry.register(name, backend_type)

    def create_backend(
        self,
        config: Any = "mock",
        parameters: Optional[Mapping[str, Any]] = None,
    ) -> BaseLocalizationBackend:
        """定位模块的统一接口和数据流处理。"""
        name, config_parameters = self._parse_config(config)
        merged_parameters = dict(config_parameters)
        if parameters is not None:
            merged_parameters.update(parameters)
        try:
            backend_type = self._registry.get(name)
            return backend_type(**merged_parameters)
        except LocalizationException:
            raise
        except Exception as exc:
            raise LocalizationException(
                "backend creation failed",
                code="BACKEND_CREATE_FAILED",
            ) from exc

    def _parse_config(self, config: Any) -> tuple[str, Mapping[str, Any]]:
        """定位模块的统一接口和数据流处理。"""
        if isinstance(config, str):
            return self._normalize_name(config), {}
        if isinstance(config, Mapping):
            name = config.get(
                "backend_type",
                config.get("backend_name", config.get("name", "MOCK")),
            )
            parameters = config.get(
                "parameters",
                config.get("backend_parameters", {}),
            )
            return self._normalize_name(str(name)), dict(parameters)
        name = getattr(
            config,
            "backend_type",
            getattr(config, "backend_name", "MOCK"),
        )
        if hasattr(config, "to_backend_parameters"):
            parameters = config.to_backend_parameters()
        else:
            parameters = getattr(
                config,
                "parameters",
                getattr(config, "backend_parameters", {}),
            )
        return self._normalize_name(str(name)), dict(parameters)

    @staticmethod
    def _normalize_name(name: str) -> str:
        """定位模块的统一接口和数据流处理。"""
        return str(name).strip().lower().replace("-", "_")

    def register(
        self,
        name: str,
        backend_type: type[BaseLocalizationBackend],
    ) -> None:
        """定位模块的统一接口和数据流处理。"""
        self._registry.register(name, backend_type)

    def get_registry(self) -> BackendRegistry:
        """定位模块的统一接口和数据流处理。"""
        return self._registry
