"""幸存者内存管理器。"""

from typing import Dict, List

from ..models.survivor import Survivor


class SurvivorMemory:
    """在内存中维护 Survivor 历史记录。"""

    def __init__(self) -> None:
        """初始化空的幸存者内存。"""
        self._survivors: Dict[str, Survivor] = {}

    def add(self, survivor: Survivor) -> None:
        """添加或保存一个 Survivor。

        Args:
            survivor: 待保存的幸存者模型。
        """
        self._survivors[survivor.survivor_id] = survivor

    def update(self, survivor: Survivor) -> None:
        """更新一个 Survivor 的内存记录。

        Args:
            survivor: 待更新的幸存者模型。
        """
        self._survivors[survivor.survivor_id] = survivor

    def remove(self, survivor_id: str) -> bool:
        """移除指定的 Survivor。

        Args:
            survivor_id: 幸存者业务标识。

        Returns:
            成功移除时返回 True，否则返回 False。
        """
        return self._survivors.pop(survivor_id, None) is not None

    def contains(self, survivor_id: str) -> bool:
        """检查内存中是否存在指定 Survivor。

        Args:
            survivor_id: 幸存者业务标识。

        Returns:
            存在时返回 True，否则返回 False。
        """
        return survivor_id in self._survivors

    def get(self, survivor_id: str) -> Survivor | None:
        """获取指定 Survivor。

        Args:
            survivor_id: 幸存者业务标识。

        Returns:
            对应的 Survivor，不存在时返回 None。
        """
        return self._survivors.get(survivor_id)

    def get_all(self) -> List[Survivor]:
        """返回内存中的全部 Survivor。"""
        return list(self._survivors.values())

    def clear(self) -> None:
        """清空全部 Survivor 内存记录。"""
        self._survivors.clear()

    def reset(self) -> None:
        """重置幸存者内存。"""
        self.clear()
