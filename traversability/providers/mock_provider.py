"""使用 Analyzer 的模拟 Traversability Provider。"""

from copy import deepcopy
from typing import Any, Mapping, Optional, Union

from traversability.analyzers import BaseTraversabilityAnalyzer
from traversability.analyzers import RuleBasedTraversabilityAnalyzer
from traversability.context import AnalyzerContext
from traversability.core import TraversabilityStatus
from traversability.exceptions import (
    ProviderException,
    TraversabilityException,
)
from traversability.interfaces import BaseTraversabilityProvider
from traversability.models import TraversabilityGrid, TraversabilityInput


class MockTraversabilityProvider(BaseTraversabilityProvider):
    """调用注入的 Analyzer 生成模拟可通过性结果。"""

    def __init__(
        self,
        grid: Optional[TraversabilityGrid] = None,
        analyzer: Optional[BaseTraversabilityAnalyzer] = None,
        default_input: Optional[
            Union[TraversabilityInput, Mapping[str, Any]]
        ] = None,
    ) -> None:
        """创建 Provider，并注入可替换的 Analyzer。"""
        if grid is not None and not isinstance(grid, TraversabilityGrid):
            raise TypeError("grid 必须是 TraversabilityGrid 实例")
        if analyzer is not None and not isinstance(
            analyzer,
            BaseTraversabilityAnalyzer,
        ):
            raise TypeError("analyzer 必须实现 BaseTraversabilityAnalyzer")
        self._analyzer = analyzer or RuleBasedTraversabilityAnalyzer()
        self._result: Optional[TraversabilityGrid] = None
        self._default_input = self._build_default_input(
            grid,
            default_input,
        )
        self._status = TraversabilityStatus.IDLE

    def analyze(self, input_data: Any = None) -> TraversabilityGrid:
        """将统一输入交给 Analyzer 并保存分析结果。"""
        self._set_status(TraversabilityStatus.RUNNING)
        analysis_input = (
            self._default_input if input_data is None else input_data
        )
        try:
            if isinstance(analysis_input, Mapping):
                analysis_input = self._mapping_to_input(analysis_input)
            if not isinstance(analysis_input, TraversabilityInput):
                raise ProviderException(
                    "Provider 输入类型无效",
                    code="INPUT_TYPE_INVALID",
                )
            analysis_input.validate()
            context = AnalyzerContext(
                timestamp=analysis_input.timestamp,
                frame_id=analysis_input.frame_id,
                input_data=analysis_input.copy(),
            )
            self._analyzer.initialize(context)
            self._analyzer.start()
            result = self._analyzer.analyze(analysis_input)
            if not isinstance(result, TraversabilityGrid):
                raise ProviderException(
                    "Analyzer 返回类型无效",
                    code="ANALYZER_RESULT_INVALID",
                )
            self._result = result.copy()
            self._set_status(TraversabilityStatus.SUCCESS)
            return self._result.copy()
        except ProviderException:
            self._set_status(TraversabilityStatus.FAILED)
            raise
        except TraversabilityException as exc:
            self._set_status(TraversabilityStatus.FAILED)
            raise ProviderException(exc.message, code=exc.code) from exc
        except Exception as exc:
            self._set_status(TraversabilityStatus.ERROR)
            raise ProviderException(
                "Traversability Analyzer 调用失败",
                code="ANALYZER_FAILED",
            ) from exc

    def get_result(self) -> Optional[TraversabilityGrid]:
        """返回最近一次分析结果的独立副本。"""
        return self._result.copy() if self._result is not None else None

    def reset(self) -> None:
        """重置 Analyzer、Provider 结果和状态。"""
        self._analyzer.reset()
        self._result = None
        self._set_status(TraversabilityStatus.IDLE)

    def _mapping_to_input(
        self,
        input_data: Mapping[str, Any],
    ) -> TraversabilityInput:
        """将旧版映射输入转换为统一输入模型。"""
        payload = deepcopy(dict(input_data))
        if "data" not in payload:
            if "occupancy" in payload:
                payload["data"] = payload["occupancy"]
                payload.setdefault("sensor_type", "occupancy")
            elif "depth" in payload:
                payload["data"] = payload["depth"]
                payload.setdefault("sensor_type", "depth")
        values = payload.get("data", [])
        payload.setdefault("width", len(values))
        payload.setdefault("height", 1)
        payload.setdefault("resolution", 1.0)
        return TraversabilityInput.from_dict(payload)

    def _build_default_input(
        self,
        grid: Optional[TraversabilityGrid],
        default_input: Optional[
            Union[TraversabilityInput, Mapping[str, Any]]
        ],
    ) -> TraversabilityInput:
        """构造未显式传入数据时使用的统一输入。"""
        if default_input is not None:
            if isinstance(default_input, TraversabilityInput):
                return default_input.copy()
            if isinstance(default_input, Mapping):
                return self._mapping_to_input(default_input)
            raise TypeError("default_input 类型无效")
        if grid is None:
            return TraversabilityInput(
                sensor_type="occupancy",
                width=1,
                height=1,
                resolution=1.0,
                data=[0.0],
            )
        occupancy = [
            0.0 if value >= 1.0 else 100.0 if value <= 0.0 else 25.0
            for value in grid.data
        ]
        return TraversabilityInput(
            timestamp=grid.timestamp,
            frame_id=grid.frame_id,
            sensor_type="occupancy",
            width=grid.width,
            height=grid.height,
            resolution=grid.resolution,
            data=occupancy,
        )
