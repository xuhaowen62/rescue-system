"""可通过性多模态处理模块。"""

from typing import Mapping, Sequence

from traversability.encoders import BaseEncoder
from traversability.fusion import BaseFeatureFusion
from traversability.models import SensorData, TraversabilityGrid
from traversability.predictors import BasePredictor


class MultiModalPipeline:
    """定义本模块的统一接口或数据结构。"""

    def __init__(
        self,
        encoders: Mapping[str, BaseEncoder],
        fusion: BaseFeatureFusion,
        predictor: BasePredictor,
    ) -> None:
        """定义本模块的统一接口或数据结构。"""
        if not encoders:
            raise ValueError("encoders ????")
        if not all(isinstance(encoder, BaseEncoder)
                   for encoder in encoders.values()):
            raise TypeError("encoders ??? BaseEncoder ????")
        if not isinstance(fusion, BaseFeatureFusion):
            raise TypeError("fusion ???? BaseFeatureFusion")
        if not isinstance(predictor, BasePredictor):
            raise TypeError("predictor ???? BasePredictor")
        self._encoders = {
            str(sensor_type).strip().lower(): encoder
            for sensor_type, encoder in encoders.items()
        }
        self._fusion = fusion
        self._predictor = predictor

    def run(self, sensor_data: Sequence[SensorData]) -> TraversabilityGrid:
        """执行本模块定义的标准处理步骤。"""
        if not sensor_data:
            raise ValueError("sensor_data ????")
        features = []
        for item in sensor_data:
            if not isinstance(item, SensorData) or not item.is_valid():
                raise ValueError("sensor_data ?????? SensorData")
            encoder = self._encoders.get(item.sensor_type.lower())
            if encoder is None:
                raise ValueError(
                    f"??????????? Encoder: {item.sensor_type}"
                )
            features.append(encoder.encode(item.copy()))
        fused_feature = self._fusion.fuse(features)
        return self._predictor.predict(fused_feature)

    def process(
        self,
        sensor_data: Sequence[SensorData],
    ) -> TraversabilityGrid:
        """定义本模块的统一接口或数据结构。"""
        return self.run(sensor_data)

    def reset(self) -> None:
        """执行本模块定义的标准处理步骤。"""
        for encoder in self._encoders.values():
            encoder.reset()
