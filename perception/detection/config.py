"""检测配置定义以及模型路径约定。"""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, Sequence, Tuple, Union


ImageSize = Union[int, Tuple[int, int]]
ModelPath = Union[str, Path]
ModelFormat = Literal["pt", "onnx", "engine", "torchscript"]
MODEL_WEIGHTS_DIR: Path = Path("perception") / "models" / "weights"


@dataclass
class DetectionConfig:
    """检测模块共享的配置对象。

    该配置类只保存检测流程需要的公开参数，不负责模型加载、推理执行
    或结果解析。模型路径使用相对项目根目录的路径，避免绑定到某台机器
    的绝对路径。

    属性:
        model_path: 模型权重文件路径，默认位于项目的模型权重目录。
        confidence_threshold: YOLO 置信度阈值。
        iou_threshold: YOLO 非极大值抑制使用的 IoU 阈值。
        device: 推理设备标识，例如 ``"cpu"`` 或 ``"0"``。
        image_size: 传递给 YOLO 的输入尺寸，可以是整数或 ``(height, width)``。
        classes: 可选的类别编号过滤器。``None`` 表示不过滤，空序列也可用。
        model_format: 模型文件格式，为后续支持多种模型后端预留配置入口。
    """

    model_path: ModelPath = MODEL_WEIGHTS_DIR / "yolov8n.pt"
    confidence_threshold: float = 0.25
    iou_threshold: float = 0.45
    device: str = "cpu"
    image_size: ImageSize = 640
    classes: Optional[Sequence[int]] = None
    model_format: ModelFormat = "pt"

    # TODO：后续通过 model_format 统一切换 YOLO11、YOLO12、ONNX 和 TensorRT 模型。



