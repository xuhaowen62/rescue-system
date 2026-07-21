"""Mission 事件管理器接口。"""


class EventManager:
    """管理 Mission 事件的接口占位。"""

    def __init__(self) -> None:
        """初始化事件管理器。"""
        self._initialized = True

    def reset(self) -> None:
        """重置事件管理器状态。

        Raises:
            NotImplementedError: 当前阶段尚未实现事件管理逻辑。
        """
        raise NotImplementedError("事件管理器的重置逻辑尚未实现。")

    def clear(self) -> None:
        """清空事件管理器内容。

        Raises:
            NotImplementedError: 当前阶段尚未实现事件管理逻辑。
        """
        raise NotImplementedError("事件管理器的清空逻辑尚未实现。")
