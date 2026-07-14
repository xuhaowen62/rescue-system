import argparse
import sys
import time
from pathlib import Path

import cv2

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.file_utils import timestamp_token, timestamped_output_path


def parse_source(value: str):
    value = str(value).strip()
    return int(value) if value.isdigit() else value


def resolve_output_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if not path.suffix:
        path = path.with_suffix('.mp4')
    return timestamped_output_path(path, default_suffix='.mp4')


def resize_keep_aspect(frame, max_width: int):
    if max_width <= 0:
        return frame
    h, w = frame.shape[:2]
    if w <= max_width:
        return frame
    scale = max_width / float(w)
    return cv2.resize(frame, (max_width, max(1, int(h * scale))), interpolation=cv2.INTER_AREA)


def open_capture(source):
    if isinstance(source, int):
        cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(source)
        return cap
    return cv2.VideoCapture(source)


def main():
    parser = argparse.ArgumentParser(description='搜救系统数据采集')
    parser.add_argument('--source', type=str, default='0', help='摄像头编号或视频文件路径，默认0')
    parser.add_argument('--out-dir', type=str, default='data/raw', help='图片保存目录')
    parser.add_argument('--save-video', type=str, default='', help='可选：录制视频路径')
    parser.add_argument('--prefix', type=str, default='capture', help='图片文件名前缀')
    parser.add_argument('--max-width', type=int, default=1280, help='显示前缩放到的最大宽度')
    parser.add_argument('--mirror', action='store_true', help='镜像显示')
    args = parser.parse_args()

    source = parse_source(args.source)
    cap = open_capture(source)
    if not cap.isOpened():
        print(f'无法打开输入源：{args.source}')
        raise SystemExit(1)

    out_dir = PROJECT_ROOT / args.out_dir if not Path(args.out_dir).is_absolute() else Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    writer = None
    video_path = resolve_output_path(args.save_video) if args.save_video else None

    print('数据采集已启动：')
    print('- 按 s 保存当前帧到图片')
    print('- 按 q 或 ESC 退出')
    print('- 如需录制视频，请使用 --save-video')
    if video_path is not None:
        print(f'- 视频将保存为：{video_path}')

    while True:
        ret, frame = cap.read()
        if not ret:
            print('读取画面失败。')
            break

        if args.mirror and isinstance(source, int):
            frame = cv2.flip(frame, 1)

        frame = resize_keep_aspect(frame, args.max_width)
        h, w = frame.shape[:2]

        if video_path is not None and writer is None:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(str(video_path), fourcc, 20.0, (w, h))
            if not writer.isOpened():
                print(f'无法创建视频文件：{video_path}')
                writer = None

        if writer is not None:
            writer.write(frame)

        overlay = frame.copy()
        cv2.putText(overlay, 'Press S to save snapshot | Q/ESC to quit', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.imshow('Data Capture', overlay)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            stamp = timestamp_token()
            image_path = out_dir / f'{args.prefix}_{stamp}.png'
            cv2.imwrite(str(image_path), frame)
            print(f'已保存：{image_path}')
        elif key == ord('q') or key == 27:
            break

    cap.release()
    if writer is not None:
        writer.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()