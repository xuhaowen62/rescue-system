"""Traversability Analyzer 执行上下文。"""

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional

from traversability.core import TraversabilityStatus


@dataclass
class AnalyzerContext:
    """保存一次 Analyzer 执行所需的时间、输入、参数和状态。"""

    timestamp: Optional[float] = None
    frame_id: str = "map"
    input_data: Any = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: TraversabilityStatus = TraversabilityStatus.CREATED

    def __post_init__(self) -> None:
        """规范化上下文基础字段。"""
        if self.timestamp is not None:
            self.timestamp = float(self.timestamp)
        self.frame_id = str(self.frame_id)
        self.parameters = dict(self.parameters)
        if not isinstance(self.status, TraversabilityStatus):
            self.status = TraversabilityStatus(str(self.status))

    def update_status(self, status: TraversabilityStatus) -> None:
        """更新上下文状态。"""
        self.status = TraversabilityStatus(status)

    def copy(self) -> "AnalyzerContext":
        """返回上下文的独立副本。"""
        return deepcopy(self)

    def to_dict(self) -> Dict[str, Any]:
        """将上下文转换为字典。"""
        data = asdict(self)
        data["status"] = self.status.value
        return data

    def reset(self) -> None:
        """清空执行上下文并恢复 CREATED 状态。"""
        self.timestamp = None
        self.frame_id = ""
        self.input_data = None
        self.parameters = {}
        self.status = TraversabilityStatus.CREATED
