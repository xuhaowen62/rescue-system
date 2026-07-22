"""可通过性多模态处理模块。"""

from numbers import Real
from typing import List, Sequence

from traversability.fusion.base_fusion import BaseFeatureFusion
from traversability.models import FeatureRepresentation


class SimpleFusion(BaseFeatureFusion):
    """定义本模块的统一接口或数据结构。"""

    def fuse(
        self,
        features: Sequence[FeatureRepresentation],
    ) -> FeatureRepresentation:
        """定义本模块的统一接口或数据结构。"""
        if not features:
            raise ValueError("features ????")
        if not all(
            isinstance(feature, FeatureRepresentation)
            and feature.is_valid()
            for feature in features
        ):
            raise ValueError("features ?????? FeatureRepresentation")
        values = [self._values(feature.feature_data) for feature in features]
        if self._same_length(values):
            fused_data = [
                sum(items) / len(items)
                for items in zip(*values)
            ]
            shape = features[0].shape
        else:
            fused_data = [item for group in values for item in group]
            shape = (len(fused_data),)
        first = features[0]
        return FeatureRepresentation(
            sensor_type="fused",
            timestamp=first.timestamp,
            frame_id=first.frame_id,
            feature_data=fused_data,
            shape=shape,
            metadata={
                "source_modalities": [
                    feature.sensor_type for feature in features
                ],
                "fusion": "simple",
            },
        )

    def _values(self, data: object) -> List[float]:
        """执行本模块定义的标准处理步骤。"""
        if isinstance(data, Real):
            return [float(data)]
        if not isinstance(data, (list, tuple)):
            raise ValueError("??????????????")
        values = [float(value) for value in data]
        return values

    def _same_length(self, values: Sequence[List[float]]) -> bool:
        """执行本模块定义的标准处理步骤。"""
        first_length = len(values[0])
        return all(len(items) == first_length for items in values)
