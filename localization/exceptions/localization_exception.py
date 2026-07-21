"""Localization 基础异常。"""


class LocalizationException(Exception):
    """表示定位框架中的通用异常。"""

    def __init__(self, message: str, code: str = "LOCALIZATION_ERROR") -> None:
        """创建带有错误消息和错误码的定位异常。"""
        self.message = message
        self.code = code
        super().__init__(message)