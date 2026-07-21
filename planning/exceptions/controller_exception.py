"""Controller 异常定义。"""

from planning.exceptions.planning_exception import PlanningException


class ControllerException(PlanningException):
    """表示 Controller 调用或状态异常。"""
