"""Factory 异常定义。"""

from planning.exceptions.planning_exception import PlanningException


class FactoryException(PlanningException):
    """表示插件注册、查询或创建异常。"""
