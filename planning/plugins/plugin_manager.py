"""Planning 插件注册与创建管理器。"""

from typing import (
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Type,
    TypeVar,
    cast,
)

from planning.controller.base import BaseController
from planning.exceptions import FactoryException
from planning.planner.base import BaseGlobalPlanner, BaseLocalPlanner
from planning.plugins.plugin_base import (
    PluginFactory,
    PluginMetadataType,
    PluginRegistration,
)
from planning.plugins.plugin_metadata import (
    ControllerPluginMetadata,
    PlannerPluginMetadata,
)


PluginType = TypeVar("PluginType")


class PluginManager:
    """管理规划器和控制器插件的注册、查询与创建。"""

    def __init__(self) -> None:
        """创建空的插件注册表。"""
        self._global_planners: Dict[str, PluginRegistration] = {}
        self._local_planners: Dict[str, PluginRegistration] = {}
        self._controllers: Dict[str, PluginRegistration] = {}

    def register_global_planner(
        self,
        name: str,
        factory: Callable[..., BaseGlobalPlanner],
        metadata: Optional[PlannerPluginMetadata] = None,
    ) -> None:
        """注册一个全局规划器插件。"""
        plugin_metadata = metadata or PlannerPluginMetadata(
            name=name,
            version="0.0.0",
            author="",
            description="",
            planner_type="global",
        )
        self._register(self._global_planners, name, factory, plugin_metadata)

    def register_local_planner(
        self,
        name: str,
        factory: Callable[..., BaseLocalPlanner],
        metadata: Optional[PlannerPluginMetadata] = None,
    ) -> None:
        """注册一个局部规划器插件。"""
        plugin_metadata = metadata or PlannerPluginMetadata(
            name=name,
            version="0.0.0",
            author="",
            description="",
            planner_type="local",
        )
        self._register(self._local_planners, name, factory, plugin_metadata)

    def register_controller(
        self,
        name: str,
        factory: Callable[..., BaseController],
        metadata: Optional[ControllerPluginMetadata] = None,
    ) -> None:
        """注册一个控制器插件。"""
        plugin_metadata = metadata or ControllerPluginMetadata(
            name=name,
            version="0.0.0",
            author="",
            description="",
            controller_type="controller",
        )
        self._register(self._controllers, name, factory, plugin_metadata)

    def create_global_planner(
        self,
        name: str,
        parameters: Optional[Mapping[str, object]] = None,
    ) -> BaseGlobalPlanner:
        """根据名称和参数创建全局规划器插件。"""
        return self._create(
            self._global_planners,
            name,
            parameters,
            BaseGlobalPlanner,
        )

    def create_local_planner(
        self,
        name: str,
        parameters: Optional[Mapping[str, object]] = None,
    ) -> BaseLocalPlanner:
        """根据名称和参数创建局部规划器插件。"""
        return self._create(
            self._local_planners,
            name,
            parameters,
            BaseLocalPlanner,
        )

    def create_controller(
        self,
        name: str,
        parameters: Optional[Mapping[str, object]] = None,
    ) -> BaseController:
        """根据名称和参数创建控制器插件。"""
        return self._create(
            self._controllers,
            name,
            parameters,
            BaseController,
        )

    def list_global_planners(self) -> List[PlannerPluginMetadata]:
        """返回已注册的全局规划器元信息。"""
        return [
            registration.metadata
            for registration in self._global_planners.values()
        ]

    def list_local_planners(self) -> List[PlannerPluginMetadata]:
        """返回已注册的局部规划器元信息。"""
        return [
            registration.metadata
            for registration in self._local_planners.values()
        ]

    def list_controllers(self) -> List[ControllerPluginMetadata]:
        """返回已注册的控制器元信息。"""
        return [
            registration.metadata
            for registration in self._controllers.values()
        ]

    def _register(
        self,
        registry: Dict[str, PluginRegistration],
        name: str,
        factory: PluginFactory,
        metadata: PluginMetadataType,
    ) -> None:
        """向指定注册表写入一个插件。"""
        if not name:
            raise FactoryException("插件名称不能为空", code="PLUGIN_NAME_EMPTY")
        if name in registry:
            raise FactoryException(
                f"插件已注册: {name}",
                code="PLUGIN_ALREADY_REGISTERED",
            )
        if not callable(factory):
            raise FactoryException(
                f"插件工厂不可调用: {name}",
                code="PLUGIN_FACTORY_INVALID",
            )
        registry[name] = PluginRegistration(
            metadata=metadata,
            factory=factory,
        )

    def _create(
        self,
        registry: Dict[str, PluginRegistration],
        name: str,
        parameters: Optional[Mapping[str, object]],
        expected_type: Type[PluginType],
    ) -> PluginType:
        """从指定注册表创建并校验插件实例。"""
        registration = registry.get(name)
        if registration is None:
            raise FactoryException(
                f"未找到插件: {name}",
                code="PLUGIN_NOT_FOUND",
            )
        try:
            instance = registration.factory(**dict(parameters or {}))
        except Exception as exc:
            raise FactoryException(
                f"插件创建失败: {name}: {exc}",
                code="PLUGIN_CREATE_FAILED",
            ) from exc
        if not isinstance(instance, expected_type):
            raise FactoryException(
                f"插件类型不匹配: {name}",
                code="PLUGIN_TYPE_INVALID",
            )
        return cast(PluginType, instance)
