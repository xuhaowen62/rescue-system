"""可通过性多模态处理模块。"""

from numbers import Real
from typing import List

from traversability.models import FeatureRepresentation, TraversabilityGrid
from traversability.predictors.base_predictor import BasePredictor


class RulePredictor(BasePredictor):
    """定义本模块的统一接口或数据结构。"""

    def predict(self, feature: FeatureRepresentation) -> TraversabilityGrid:
        """执行本模块定义的标准处理步骤。"""
        if not isinstance(feature, FeatureRepresentation):
            raise TypeError("feature ??? FeatureRepresentation ??")
        if not feature.is_valid():
            raise ValueError("feature ????")
        values = self._values(feature.feature_data)
        width, height = self._grid_size(feature, len(values))
        return TraversabilityGrid(
            width=width,
            height=height,
            resolution=float(feature.metadata.get("resolution", 1.0)),
            data=[min(1.0, max(0.0, value)) for value in values],
            timestamp=feature.timestamp,
            frame_id=feature.frame_id,
        )

    def _values(self, data: object) -> List[float]:
        """执行本模块定义的标准处理步骤。"""
        if isinstance(data, Real):
            return [float(data)]
        if not isinstance(data, (list, tuple)):
            raise ValueError("feature_data ??????????")
        return [float(value) for value in data]

    def _grid_size(
        self,
        feature: FeatureRepresentation,
        data_length: int,
    ) -> tuple[int, int]:
        """定义本模块的统一接口或数据结构。"""
        if len(feature.shape) >= 2:
            height, width = feature.shape[0], feature.shape[1]
            if width * height == data_length:
                return width, height
        return data_length, 1
