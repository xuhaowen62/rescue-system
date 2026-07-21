"""Planning 插件基础定义。"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Union

from planning.plugins.plugin_metadata import (
    ControllerPluginMetadata,
    PlannerPluginMetadata,
)


PluginFactory = Callable[..., object]
PluginMetadataType = Union[
    PlannerPluginMetadata,
    ControllerPluginMetadata,
]


class BasePlugin(ABC):
    """Planning 插件统一抽象接口。"""

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadataType:
        """返回插件元信息。"""
        raise NotImplementedError


@dataclass(frozen=True)
class PluginRegistration:
    """保存插件元信息和实例工厂。"""

    metadata: PluginMetadataType
    factory: PluginFactory
