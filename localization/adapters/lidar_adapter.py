"""定位模块扩展接口。"""

from localization.adapters.base_adapter import BaseLocalizationAdapter


class LiDARLocalizationAdapter(BaseLocalizationAdapter):
    """定义本模块的统一接口或数据结构。"""

    pass


LidarLocalizationAdapter = LiDARLocalizationAdapter
