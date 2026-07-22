"""定位数据回放抽象接口。"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class ReplayInterface(ABC):
    """定义 Camera、IMU、LiDAR 和 Pose 数据回放协议。"""

    @abstractmethod
    def add_data(self, data: Any) -> None:
        """加入一条待回放数据。"""
        raise NotImplementedError

    @abstractmethod
    def read_next(self) -> Optional[Any]:
        """读取下一条数据，没有数据时返回 None。"""
        raise NotImplementedError

    @abstractmethod
    def has_next(self) -> bool:
        """判断是否还有待回放数据。"""
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        """重置回放游标。"""
        raise NotImplementedError
