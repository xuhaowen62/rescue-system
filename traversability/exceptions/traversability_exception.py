"""Traversability 基础异常。"""


class TraversabilityException(Exception):
    """表示 Traversability 框架中的通用异常。"""

    def __init__(
        self,
        message: str,
        code: str = "TRAVERSABILITY_ERROR",
    ) -> None:
        """创建带有错误消息和错误码的异常。"""
        self.message = message
        self.code = code
        super().__init__(message)