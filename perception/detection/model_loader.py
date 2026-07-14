"""检测模型加载接口及模型格式扩展预留。"""

from pathlib import Path
from typing import TYPE_CHECKING

from .config import DetectionConfig

if TYPE_CHECKING:
    from ultralytics import YOLO


class ModelLoader:
    """负责根据配置检查并加载 Ultralytics YOLO 模型。

    当前实现只保留现有的 YOLO 模型加载能力，不包含推理、结果解析、
    图像处理或 ROS2 集成。其他模型格式通过预留接口和后续任务延后实现。
    """

    def __init__(self, config: DetectionConfig) -> None:
        """保存模型加载所需的检测配置。

        参数:
            config: 包含模型路径和模型格式信息的共享检测配置。
        """
        self._config = config

    def load_model(self) -> "YOLO":
        """检查模型文件并返回已加载的 Ultralytics YOLO 实例。

        返回:
            已初始化的 Ultralytics ``YOLO`` 模型实例。

        异常:
            FileNotFoundError: 配置中的模型路径不是已存在的文件时抛出。
            ImportError: 当前环境没有安装 Ultralytics 时抛出。
        """
        model_path = Path(self._config.model_path)
        if not model_path.is_file():
            raise FileNotFoundError(
                f"YOLO 模型文件不存在：{model_path}"
            )

        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise ImportError(
                "加载 YOLO 模型需要安装 Ultralytics。"
            ) from exc

        return YOLO(str(model_path))

    # TODO：后续根据 model_format 增加 .onnx、.engine 和 TorchScript 加载接口。



