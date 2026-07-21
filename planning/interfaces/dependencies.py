"""导航外部依赖的预留接口。"""

from abc import ABC, abstractmethod
from typing import Optional

from planning.models import Goal, Path, Pose


class BaseSlamProvider(ABC):
    """SLAM 或定位模块的预留接口。"""

    @abstractmethod
    def get_current_pose(self) -> Optional[Pose]:
        """获取机器人当前位姿。"""
        raise NotImplementedError


class BaseTraversabilityProvider(ABC):
    """可通行性模块的预留接口。"""

    @abstractmethod
    def is_path_traversable(self, path: Path) -> bool:
        """判断路径是否可通行。"""
        raise NotImplementedError


class BaseMissionProvider(ABC):
    """任务模块的预留接口。"""

    @abstractmethod
    def get_active_goal(self) -> Optional[Goal]:
        """获取任务模块当前激活的导航目标。"""
        raise NotImplementedError
