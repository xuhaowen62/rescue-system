"""检测统一入口以及推理引擎依赖注入实现。"""

from typing import TYPE_CHECKING, Any, List

from .inference import InferenceEngine

if TYPE_CHECKING:
    from ultralytics.engine.results import Results


class Detector:
    """提供检测模块唯一的统一检测入口。

    Detector 通过依赖注入接收外部创建的 ``InferenceEngine``，自身不负责
    创建模型加载器、YOLO 模型或推理引擎。这样可以在不修改统一接口的情况
    下替换 YOLO、ONNX、TensorRT 或 RT-DETR 等后端实现。
    """

    def __init__(self, inference_engine: InferenceEngine) -> None:
        """保存外部注入的推理引擎。

        参数:
            inference_engine: 由外部完成配置和模型初始化的推理引擎。
        """
        self._inference_engine = inference_engine

    def detect(self, image: Any) -> List["Results"]:
        """通过注入的推理引擎对图像执行检测。

        参数:
            image: Ultralytics YOLO 支持的图像输入。

        返回:
            推理引擎返回的官方 ``Results`` 对象列表，不做解析或修改。
        """
        return self._inference_engine.predict(image)

    # TODO：后续仅在统一检测接口需要时扩展生命周期管理能力。




