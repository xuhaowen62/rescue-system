"""基于 supervision 的感知结果可视化实现。"""

from typing import TYPE_CHECKING, List, Mapping

import numpy as np
import supervision as sv
from numpy.typing import NDArray
from supervision.draw.utils import draw_text
from supervision.geometry.core import Point

if TYPE_CHECKING:
    from ultralytics.engine.results import Results


ImageArray = NDArray[np.uint8]


class Visualizer:
    """负责独立绘制检测结果、FPS 和统计信息。

    本类只依赖 supervision 完成可视化，不依赖 ROS2、跟踪 或 融合。
    每个公开绘制接口只负责一种信息，输入图像不会被原地修改。
    """

    def __init__(self) -> None:
        """初始化 supervision 标注器。"""
        self._box_annotator = sv.BoxAnnotator()
        self._label_annotator = sv.LabelAnnotator()

    def draw_detections(self, results: "Results") -> ImageArray:
        """使用 supervision 在原始图像上绘制检测框和类别标签。

        参数:
            results: Ultralytics 返回的单个 ``Results`` 对象。

        返回:
            绘制检测框和标签后的图像数组。
        """
        detections = sv.Detections.from_ultralytics(results)
        image = results.orig_img.copy()
        image = self._box_annotator.annotate(
            scene=image,
            detections=detections,
        )
        return self._label_annotator.annotate(
            scene=image,
            detections=detections,
            labels=self._build_detection_labels(results, detections),
        )

    def draw_fps(self, image: ImageArray, fps: float) -> ImageArray:
        """使用 supervision 在图像左上方绘制 FPS 信息。

        参数:
            image: 待绘制的图像数组。
            fps: 当前帧率。

        返回:
            绘制 FPS 信息后的图像数组。
        """
        return draw_text(
            scene=image.copy(),
            text=f"FPS: {fps:.1f}",
            text_anchor=Point(x=55, y=25),
            text_color=sv.Color.WHITE,
            background_color=sv.Color.BLACK,
            text_padding=8,
        )

    def draw_statistics(
        self,
        image: ImageArray,
        target_count: int,
        class_statistics: Mapping[str, int],
    ) -> ImageArray:
        """使用 supervision 在图像上绘制目标总数和类别统计信息。

        参数:
            image: 待绘制的图像数组。
            target_count: 当前检测到的目标总数。
            class_statistics: 类别名称到目标数量的映射。

        返回:
            绘制统计信息后的图像数组。
        """
        annotated_image = image.copy()
        statistics = [f"Targets: {target_count}"]
        statistics.extend(
            f"{class_name}: {count}"
            for class_name, count in class_statistics.items()
        )
        for index, text in enumerate(statistics):
            annotated_image = draw_text(
                scene=annotated_image,
                text=text,
                text_anchor=Point(x=90, y=30 + index * 28),
                text_color=sv.Color.WHITE,
                background_color=sv.Color.BLACK,
                text_padding=6,
            )
        return annotated_image

    @staticmethod
    def _build_detection_labels(
        results: "Results",
        detections: sv.Detections,
    ) -> List[str]:
        """根据 Ultralytics 结果生成 supervision 所需的标签文本。

        参数:
            results: Ultralytics 返回的单个 ``Results`` 对象。
            detections: 由 supervision 转换得到的检测对象。

        返回:
            与检测对象顺序对应的类别和置信度标签列表。
        """
        if detections.class_id is None or detections.confidence is None:
            return []

        return [
            f"{results.names[int(class_id)]} {confidence:.2f}"
            for class_id, confidence in zip(
                detections.class_id,
                detections.confidence,
            )
        ]

    # TODO：后续增加目标跟踪轨迹绘制。
    # TODO：后续增加 ROI 统计功能。
    # TODO：后续增加 HeatMap 可视化功能。
    # TODO：后续增加 Polygon Zone 可视化功能。
    # TODO：后续增加 Line Counter 可视化功能。

