"""Planning 异常基类。"""


class PlanningException(Exception):
    """Planning 模块统一异常基类。"""

    def __init__(self, message: str, code: str = "PLANNING_ERROR") -> None:
        """创建带错误码的 Planning 异常。"""
        super().__init__(message)
        self.message = message
        self.code = code
