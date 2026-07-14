"""检测推理接口以及官方结果对象的原样转发。"""

from typing import TYPE_CHECKING, Any, List

from .config import DetectionConfig

if TYPE_CHECKING:
    from ultralytics import YOLO
    from ultralytics.engine.results import Results


class InferenceEngine:
    """负责调用 YOLO 推理接口并原样返回官方结果对象。

    该类只负责接收模型、接收图像以及转发推理参数，不解析 Detection
    Results，不绘制检测框，也不承担摄像头、ROS2 或其他模块的职责。
    """

    def __init__(self, model: "YOLO", config: DetectionConfig) -> None:
        """保存已加载的模型和推理配置。

        参数:
            model: 已初始化的 Ultralytics YOLO 模型实例。
            config: 用于配置 YOLO 推理参数的共享检测配置。
        """
        self._model = model
        self._config = config

    def predict(self, image: Any) -> List["Results"]:
        """对单张图像调用 ``YOLO.predict`` 并返回官方结果对象。

        参数:
            image: Ultralytics 支持的图像输入，例如 NumPy 数组、图像路径或
                其他受支持的图像源对象。

        返回:
            ``YOLO.predict`` 返回的官方 ``Results`` 对象列表，结果不会被
            解析、过滤或修改。
        """
        return self._model.predict(
            source=image,
            conf=self._config.confidence_threshold,
            iou=self._config.iou_threshold,
            device=self._config.device,
            imgsz=self._config.image_size,
            classes=self._config.classes,
        )

    # TODO：后续根据实际部署需求增加批量推理和推理上下文控制。


