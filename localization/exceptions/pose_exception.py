"""位姿相关异常。"""

from localization.exceptions.localization_exception import (
    LocalizationException,
)


class PoseException(LocalizationException):
    """表示位姿数据或位姿操作异常。"""