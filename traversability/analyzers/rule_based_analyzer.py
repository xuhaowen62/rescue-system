"""规则型 Traversability Analyzer。"""

from math import isfinite
from typing import Any, List, Mapping, Optional, Tuple

from traversability.analyzers.base_analyzer import (
    BaseTraversabilityAnalyzer,
)
from traversability.context import AnalyzerContext
from traversability.core import TraversabilityStatus
from traversability.exceptions import (
    AnalyzerException,
    TraversabilityException,
)
from traversability.models import TraversabilityGrid, TraversabilityInput


class RuleBasedTraversabilityAnalyzer(BaseTraversabilityAnalyzer):
    """根据占用或深度阈值生成透明的可通过性结果。"""

    def __init__(
        self,
        occupancy_obstacle_threshold: float = 50.0,
        occupancy_risk_threshold: float = 25.0,
        depth_obstacle_threshold: float = 0.5,
        depth_risk_threshold: float = 1.0,
    ) -> None:
        """创建规则 Analyzer 并设置输入阈值。"""
        super().__init__()
        self.occupancy_obstacle_threshold = float(
            occupancy_obstacle_threshold
        )
        self.occupancy_risk_threshold = float(occupancy_risk_threshold)
        self.depth_obstacle_threshold = float(depth_obstacle_threshold)
        self.depth_risk_threshold = float(depth_risk_threshold)
        self._last_grid: Optional[TraversabilityGrid] = None

    def analyze(self, input_data: Any) -> TraversabilityGrid:
        """根据统一输入数据生成可通过性网格。"""
        if self.get_status() in {
            TraversabilityStatus.CREATED,
            TraversabilityStatus.STOPPED,
            TraversabilityStatus.FAILED,
            TraversabilityStatus.ERROR,
        }:
            self.initialize(AnalyzerContext(input_data=input_data))
        self.start()
        try:
            (
                input_type,
                width,
                height,
                resolution,
                values,
                timestamp,
                frame_id,
            ) = self._normalize_input(input_data)
            if input_type == "depth":
                result = [
                    self._depth_to_traversability(value)
                    for value in values
                ]
            else:
                result = [
                    self._occupancy_to_traversability(value)
                    for value in values
                ]
            grid = TraversabilityGrid(
                width=width,
                height=height,
                resolution=resolution,
                data=result,
                timestamp=timestamp,
                frame_id=frame_id,
            )
            self._last_grid = grid.copy()
            self._set_status(TraversabilityStatus.SUCCESS)
            return grid
        except (AnalyzerException, TraversabilityException):
            self._set_status(TraversabilityStatus.FAILED)
            raise
        except Exception as exc:
            self._set_status(TraversabilityStatus.ERROR)
            raise AnalyzerException(
                "规则 Analyzer 分析失败",
                code="ANALYZER_FAILED",
            ) from exc

    def reset(self) -> None:
        """清除最近一次分析结果并恢复 CREATED 状态。"""
        self._last_grid = None
        self._context = None
        self._set_status(TraversabilityStatus.CREATED)

    def _normalize_input(
        self,
        input_data: Any,
    ) -> Tuple[
        str,
        int,
        int,
        float,
        List[float],
        Optional[float],
        str,
    ]:
        """将兼容格式转换为统一输入并执行一致性检查。"""
        if isinstance(input_data, Mapping):
            payload = dict(input_data)
            if "data" not in payload:
                if "occupancy" in payload:
                    payload["data"] = payload["occupancy"]
                    payload["sensor_type"] = "occupancy"
                elif "depth" in payload:
                    payload["data"] = payload["depth"]
                    payload["sensor_type"] = "depth"
            values = payload.get("data", [])
            payload.setdefault("width", len(values))
            payload.setdefault("height", 1)
            payload.setdefault("resolution", 1.0)
            input_data = TraversabilityInput.from_dict(payload)
        if not isinstance(input_data, TraversabilityInput):
            raise AnalyzerException(
                "输入必须是 TraversabilityInput 或映射对象",
                code="INPUT_TYPE_INVALID",
            )
        input_data.validate()
        input_type = input_data.sensor_type.lower()
        if input_type not in {"occupancy", "depth"}:
            raise AnalyzerException(
                "sensor_type 仅支持 occupancy 或 depth",
                code="SENSOR_TYPE_INVALID",
            )
        values = [float(value) for value in input_data.data]
        if not values or not all(isfinite(value) for value in values):
            raise AnalyzerException(
                "输入 data 必须是有限数值序列",
                code="INPUT_DATA_INVALID",
            )
        return (
            input_type,
            input_data.width,
            input_data.height,
            input_data.resolution,
            values,
            input_data.timestamp,
            input_data.frame_id,
        )

    def _occupancy_to_traversability(self, value: float) -> float:
        """将占用值按阈值映射为可通过性值。"""
        if value < 0.0:
            return 0.5
        if value >= self.occupancy_obstacle_threshold:
            return 0.0
        if value >= self.occupancy_risk_threshold:
            return 0.5
        return 1.0

    def _depth_to_traversability(self, value: float) -> float:
        """将深度值按距离阈值映射为可通过性值。"""
        if value <= 0.0 or value < self.depth_obstacle_threshold:
            return 0.0
        if value < self.depth_risk_threshold:
            return 0.5
        return 1.0
