import argparse
import sys
import time
from pathlib import Path

import cv2

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.file_utils import timestamped_output_path


def resize_keep_aspect(frame, max_width=960):
    h, w = frame.shape[:2]
    if w <= max_width:
        return frame
    scale = max_width / float(w)
    new_size = (max_width, int(h * scale))
    return cv2.resize(frame, new_size)


def resolve_save_path(save_value: str) -> Path | None:
    raw = str(save_value).strip()
    if not raw:
        return None
    path = Path(raw)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if not path.suffix:
        path = path.with_suffix('.mp4')
    return timestamped_output_path(path, default_suffix='.mp4')


def main():
    parser = argparse.ArgumentParser(description='Webcam person detection using OpenCV HOG')
    parser.add_argument('--camera', type=int, default=0, help='摄像头编号，默认0')
    parser.add_argument('--max-width', type=int, default=960, help='检测前缩放到的最大宽度')
    parser.add_argument('--save', type=str, default='', help='可选：保存输出视频路径，例如 results/output.mp4')
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(args.camera)

    if not cap.isOpened():
        print('无法打开摄像头，请检查摄像头编号或权限。')
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    writer = None
    save_path = resolve_save_path(args.save)
    prev_time = time.time()
    fps = 0.0

    if save_path is not None:
        print(f'视频将保存为：{save_path}')

    print('开始检测，按 q 或 ESC 退出。')

    while True:
        ret, frame = cap.read()
        if not ret:
            print('读取摄像头画面失败。')
            break

        frame = resize_keep_aspect(frame, args.max_width)

        rects, weights = hog.detectMultiScale(
            frame,
            winStride=(8, 8),
            padding=(8, 8),
            scale=1.05,
        )

        boxes = []
        scores = []
        for (x, y, w, h), weight in zip(rects, weights):
            boxes.append([int(x), int(y), int(w), int(h)])
            scores.append(float(weight))

        indices = []
        if boxes:
            indices = cv2.dnn.NMSBoxes(
                bboxes=boxes,
                scores=scores,
                score_threshold=0.3,
                nms_threshold=0.4,
            )

        person_count = 0
        if len(indices) > 0:
            for i in indices.flatten():
                x, y, w, h = boxes[i]
                score = scores[i]
                person_count += 1

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    f'person {score:.2f}',
                    (x, max(20, y - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )

        now = time.time()
        dt = now - prev_time
        prev_time = now
        if dt > 0:
            fps = 0.9 * fps + 0.1 * (1.0 / dt) if fps > 0 else (1.0 / dt)

        cv2.putText(
            frame,
            f'Persons: {person_count} | FPS: {fps:.1f}',
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2,
        )

        cv2.imshow('Person Detection', frame)

        if save_path is not None and writer is None:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            h, w = frame.shape[:2]
            writer = cv2.VideoWriter(str(save_path), fourcc, 20.0, (w, h))
            if not writer.isOpened():
                print(f'无法创建视频文件：{save_path}')
                writer = None

        if writer is not None:
            writer.write(frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

    cap.release()
    if writer is not None:
        writer.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()