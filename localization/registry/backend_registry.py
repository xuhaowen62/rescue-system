"""定位模块的统一接口和数据流处理。"""

from typing import Dict, List, Type

from localization.backends.base_backend import BaseLocalizationBackend
from localization.exceptions import LocalizationException


class BackendRegistry:
    """定位模块的统一接口和数据流处理。"""

    def __init__(self) -> None:
        """定位模块的统一接口和数据流处理。"""
        self._backends: Dict[str, Type[BaseLocalizationBackend]] = {}

    def register(
        self,
        name: str,
        backend_type: Type[BaseLocalizationBackend],
    ) -> None:
        """定位模块的统一接口和数据流处理。"""
        key = str(name).strip().lower()
        if not key:
            raise LocalizationException(
                "backend name is invalid",
                code="BACKEND_NAME_INVALID",
            )
        if not isinstance(backend_type, type) or not issubclass(
            backend_type, BaseLocalizationBackend
        ):
            raise LocalizationException(
                "backend type is invalid",
                code="BACKEND_TYPE_INVALID",
            )
        self._backends[key] = backend_type

    def get(self, name: str) -> Type[BaseLocalizationBackend]:
        """定位模块的统一接口和数据流处理。"""
        key = str(name).strip().lower()
        try:
            return self._backends[key]
        except KeyError as exc:
            raise LocalizationException(
                f"backend is not registered: {name}",
                code="BACKEND_NOT_FOUND",
            ) from exc

    def list(self) -> List[str]:
        """定位模块的统一接口和数据流处理。"""
        return sorted(self._backends)
