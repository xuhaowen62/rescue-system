"""Goal 异常定义。"""

from planning.exceptions.planning_exception import PlanningException


class GoalException(PlanningException):
    """表示 Goal 数据或 Goal 生命周期异常。"""
