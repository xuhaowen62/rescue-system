"""Localization 到 Planning 的位姿适配接口。"""

from abc import ABC, abstractmethod
from typing import Optional

from localization.models import PoseState


class BasePlanningAdapter(ABC):
    """定义 Planning 读取 Localization 位姿的最小协议。"""

    @abstractmethod
    def get_pose(self) -> Optional[PoseState]:
        """向 Planning 提供当前位姿。"""
        raise NotImplementedError