"""Planning Controller Factory。"""

from typing import Mapping, Optional

from planning.controller.base import BaseController
from planning.plugins.plugin_manager import PluginManager


class ControllerFactory:
    """仅依赖 Controller 接口和插件管理器的控制器工厂。"""

    def __init__(self, plugin_manager: PluginManager) -> None:
        """创建 Controller Factory。"""
        self._plugin_manager = plugin_manager

    def create_controller(
        self,
        name: str,
        parameters: Optional[Mapping[str, object]] = None,
    ) -> BaseController:
        """创建指定名称的控制器。"""
        return self._plugin_manager.create_controller(name, parameters)
