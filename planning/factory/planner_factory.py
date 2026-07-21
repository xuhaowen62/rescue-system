"""Planning Planner Factory。"""

from typing import Mapping, Optional

from planning.controller.base import BaseController
from planning.planner.base import BaseGlobalPlanner, BaseLocalPlanner
from planning.plugins.plugin_manager import PluginManager


class PlannerFactory:
    """仅依赖抽象接口和插件管理器的统一工厂。"""

    def __init__(self, plugin_manager: PluginManager) -> None:
        """创建 Planner Factory。"""
        self._plugin_manager = plugin_manager

    def create_global_planner(
        self,
        name: str,
        parameters: Optional[Mapping[str, object]] = None,
    ) -> BaseGlobalPlanner:
        """创建指定名称的全局规划器。"""
        return self._plugin_manager.create_global_planner(name, parameters)

    def create_local_planner(
        self,
        name: str,
        parameters: Optional[Mapping[str, object]] = None,
    ) -> BaseLocalPlanner:
        """创建指定名称的局部规划器。"""
        return self._plugin_manager.create_local_planner(name, parameters)

    def create_controller(
        self,
        name: str,
        parameters: Optional[Mapping[str, object]] = None,
    ) -> BaseController:
        """创建指定名称的控制器。"""
        return self._plugin_manager.create_controller(name, parameters)
