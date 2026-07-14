import argparse
import sys
import time
from collections import deque
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.file_utils import timestamped_output_path

try:
    from ultralytics import YOLO
except ImportError as exc:
    YOLO = None
    ULTRALYTICS_IMPORT_ERROR = exc
else:
    ULTRALYTICS_IMPORT_ERROR = None


DEFAULT_MODEL = PROJECT_ROOT / 'models' / 'weights' / 'yolov8n.pt'
DEFAULT_SNAPSHOT_DIR = PROJECT_ROOT / 'results' / 'images'
WINDOW_NAME = 'Rescue System | Person Detection'


def parse_source(value: str):
    value = str(value).strip()
    return int(value) if value.isdigit() else value


def resolve_model_path(model_value: str) -> str:
    raw = str(model_value).strip() or str(DEFAULT_MODEL)
    candidate = Path(raw)
    search_paths = []
    if candidate.is_absolute():
        search_paths.append(candidate)
    else:
        search_paths.extend([
            PROJECT_ROOT / candidate,
            PROJECT_ROOT / 'models' / 'weights' / candidate.name,
            Path.cwd() / candidate,
            candidate,
        ])

    for path in search_paths:
        if path.exists():
            return str(path.resolve())
    return str(candidate)


def resolve_output_path(save_value: str) -> Path:
    path = Path(save_value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if not path.suffix:
        path = path.with_suffix('.mp4')
    return timestamped_output_path(path, default_suffix='.mp4')


def resolve_output_dir(dir_value: str) -> Path:
    path = Path(dir_value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    path.mkdir(parents=True, exist_ok=True)
    return path


def resize_keep_aspect(frame, max_width: int):
    if max_width <= 0:
        return frame
    h, w = frame.shape[:2]
    if w <= max_width:
        return frame
    scale = max_width / float(w)
    new_h = max(1, int(h * scale))
    return cv2.resize(frame, (max_width, new_h), interpolation=cv2.INTER_AREA)


def open_capture(source):
    if isinstance(source, int):
        cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(source)
        return cap
    return cv2.VideoCapture(source)


def draw_text(img, text, org, color, scale=0.6, thickness=1):
    cv2.putText(
        img,
        text,
        org,
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        thickness,
        cv2.LINE_AA,
    )


def draw_box(img, x1, y1, x2, y2, color, alpha=0.20):
    overlay = img.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)


def draw_card(canvas, x, y, w, title, lines, accent):
    title_h = 34
    line_h = 24
    pad = 14
    h = title_h + pad + len(lines) * line_h + 12

    cv2.rectangle(canvas, (x, y), (x + w, y + h), (28, 34, 44), -1)
    cv2.rectangle(canvas, (x, y), (x + w, y + 5), accent, -1)
    cv2.rectangle(canvas, (x, y), (x + w, y + h), (60, 66, 78), 1)
    draw_text(canvas, title, (x + 14, y + 23), (255, 255, 255), 0.7, 2)

    cy = y + title_h + 6
    for line in lines:
        draw_text(canvas, line, (x + 14, cy), (228, 228, 228), 0.55, 1)
        cy += line_h
    return h


def short_text(text, limit=42):
    text = str(text)
    if len(text) <= limit:
        return text
    return text[: limit - 3] + '...'


def time_label() -> str:
    return datetime.now().strftime('%H:%M:%S')


def push_event(events: deque[str], message: str):
    events.appendleft(f'[{time_label()}] {message}')


def annotate_frame(frame, result, target_person_only: bool):
    annotated = frame.copy()
    person_count = 0
    shown_count = 0

    if result.boxes is None or len(result.boxes) == 0:
        return annotated, person_count, shown_count

    for box in result.boxes:
        cls_id = int(box.cls.item())
        conf = float(box.conf.item())
        if target_person_only and cls_id != 0:
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        class_name = result.names.get(cls_id, str(cls_id))
        color = (0, 220, 0) if cls_id == 0 else (0, 180, 255)

        draw_box(annotated, x1, y1, x2, y2, color, alpha=0.15)
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        label = f'{class_name} {conf:.2f}'
        label_y = max(24, y1 - 8)
        label_w = min(220, max(120, len(label) * 10))
        cv2.rectangle(annotated, (x1, label_y - 20), (x1 + label_w, label_y + 4), (10, 10, 10), -1)
        cv2.rectangle(annotated, (x1, label_y - 20), (x1 + label_w, label_y + 4), color, 1)
        draw_text(annotated, label, (x1 + 6, label_y - 4), (255, 255, 255), 0.55, 1)

        shown_count += 1
        if cls_id == 0:
            person_count += 1

    return annotated, person_count, shown_count


def compose_dashboard(frame, stats, settings, snapshot_text, save_text, events, paused):
    frame_h, frame_w = frame.shape[:2]
    header_h = 84
    footer_h = 56
    sidebar_w = 392
    canvas = np.full((header_h + frame_h + footer_h, frame_w + sidebar_w, 3), (17, 20, 26), dtype=np.uint8)

    # Header
    cv2.rectangle(canvas, (0, 0), (canvas.shape[1], header_h), (28, 42, 66), -1)
    cv2.rectangle(canvas, (0, header_h - 4), (canvas.shape[1], header_h), (0, 174, 255), -1)
    draw_text(canvas, 'RESCUE SYSTEM / FIND-PERSON CONSOLE', (18, 34), (255, 255, 255), 0.88, 2)
    draw_text(canvas, 'Multi-modal rescue project ? people-only detection terminal', (20, 60), (214, 214, 214), 0.56, 1)

    if paused:
        status_text = 'PAUSED'
        status_color = (130, 130, 130)
    elif stats['persons'] > 0:
        status_text = 'PERSON DETECTED'
        status_color = (0, 170, 0)
    else:
        status_text = 'SEARCHING'
        status_color = (0, 174, 255)

    badge_w = 250
    badge_x = canvas.shape[1] - badge_w - 18
    cv2.rectangle(canvas, (badge_x, 18), (badge_x + badge_w, 52), status_color, -1)
    cv2.rectangle(canvas, (badge_x, 18), (badge_x + badge_w, 52), (255, 255, 255), 1)
    draw_text(canvas, status_text, (badge_x + 16, 42), (0, 0, 0), 0.84, 2)
    draw_text(canvas, time_label(), (badge_x + 16, 70), (230, 230, 230), 0.52, 1)

    # Frame area
    frame_y = header_h
    canvas[frame_y:frame_y + frame_h, 0:frame_w] = frame
    cv2.rectangle(canvas, (0, frame_y), (frame_w - 1, frame_y + frame_h - 1), (64, 72, 84), 1)

    # Frame overlay stats
    overlay_x = 16
    overlay_y = frame_y + 16
    stat_items = [
        ('Persons', str(stats['persons'])),
        ('Boxes', str(stats['shown'])),
        ('FPS', f'{stats["fps"]:.1f}'),
    ]
    for idx, (label, value) in enumerate(stat_items):
        bx = overlay_x + idx * 132
        cv2.rectangle(canvas, (bx, overlay_y), (bx + 118, overlay_y + 56), (0, 0, 0), -1)
        cv2.rectangle(canvas, (bx, overlay_y), (bx + 118, overlay_y + 56), (0, 174, 255), 1)
        draw_text(canvas, label, (bx + 12, overlay_y + 22), (190, 190, 190), 0.5, 1)
        draw_text(canvas, value, (bx + 12, overlay_y + 44), (255, 255, 255), 0.8, 2)

    if stats['persons'] > 0:
        cv2.rectangle(canvas, (16, frame_y + frame_h - 66), (frame_w - 16, frame_y + frame_h - 20), (0, 70, 170), -1)
        cv2.rectangle(canvas, (16, frame_y + frame_h - 66), (frame_w - 16, frame_y + frame_h - 20), (0, 220, 0), 2)
        draw_text(canvas, 'ALERT: person target detected in the current scene', (32, frame_y + frame_h - 36), (255, 255, 255), 0.72, 2)
    else:
        cv2.rectangle(canvas, (16, frame_y + frame_h - 66), (frame_w - 16, frame_y + frame_h - 20), (38, 44, 54), -1)
        cv2.rectangle(canvas, (16, frame_y + frame_h - 66), (frame_w - 16, frame_y + frame_h - 20), (80, 88, 98), 1)
        draw_text(canvas, 'No person found yet. The system keeps scanning.', (32, frame_y + frame_h - 36), (230, 230, 230), 0.68, 1)

    # Sidebar cards
    x = frame_w + 18
    y = header_h + 16
    card_w = sidebar_w - 36

    status_color = (0, 170, 0) if stats['persons'] > 0 else (0, 174, 255)
    if paused:
        status_color = (130, 130, 130)

    mission_lines = [
        f'State: {status_text}',
        f'Persons: {stats["persons"]}',
        f'Boxes: {stats["shown"]}',
        f'FPS: {stats["fps"]:.1f}',
        f'Recording: {"ON" if settings["save_video"] else "OFF"}',
    ]
    y += draw_card(canvas, x, y, card_w, 'MISSION STATUS', mission_lines, status_color) + 12

    scene_lines = [
        f'Source: {short_text(settings["source_text"], 36)}',
        f'Model: {short_text(Path(settings["model_path"]).name, 30)}',
        f'Mode: {settings["display_mode"]}',
        f'Image size: {settings["imgsz"]}',
        f'Conf / IOU: {settings["conf"]:.2f} / {settings["iou"]:.2f}',
        f'Device: {settings["device_text"]}',
        f'Mirror: {settings["mirror_text"]}',
    ]
    y += draw_card(canvas, x, y, card_w, 'SCENE SETTINGS', scene_lines, (0, 174, 255)) + 12

    output_lines = [
        f'Video: {short_text(save_text, 30)}',
        f'Snapshot: {short_text(snapshot_text, 30)}',
        f'Image dir: {short_text(str(settings["snapshot_dir"]), 28)}',
        'Naming rule: always timestamped',
        'Overwrite: disabled',
    ]
    y += draw_card(canvas, x, y, card_w, 'OUTPUT POLICY', output_lines, (255, 146, 0)) + 12

    log_lines = list(events)[:5]
    if not log_lines:
        log_lines = ['[--:--:--] Waiting for events...']
    y += draw_card(canvas, x, y, card_w, 'EVENT LOG', log_lines, (170, 90, 255)) + 12

    control_lines = [
        'Q / ESC : Exit',
        'P       : Pause / Resume',
        'S       : Save snapshot',
        'Find-person only; no interaction module',
    ]
    y += draw_card(canvas, x, y, card_w, 'CONTROLS', control_lines, (255, 146, 0)) + 12

    # Footer
    footer_y = header_h + frame_h
    cv2.rectangle(canvas, (0, footer_y), (canvas.shape[1], canvas.shape[0]), (24, 28, 35), -1)
    cv2.rectangle(canvas, (0, footer_y), (canvas.shape[1], footer_y + 4), (0, 174, 255), -1)
    draw_text(canvas, 'Project scope: find people only.', (18, footer_y + 33), (220, 220, 220), 0.62, 1)
    draw_text(canvas, 'Saved files use time-stamped names and never overwrite old versions.', (380, footer_y + 33), (220, 220, 220), 0.58, 1)

    if paused:
        overlay = canvas.copy()
        cv2.rectangle(overlay, (0, header_h), (frame_w, header_h + frame_h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.22, canvas, 0.78, 0, canvas)
        draw_text(canvas, 'PAUSED', (frame_w // 2 - 70, header_h + frame_h // 2), (255, 255, 255), 1.2, 3)

    return canvas


def main():
    parser = argparse.ArgumentParser(description='YOLO person detection dashboard')
    parser.add_argument('--source', type=str, default='0', help='Camera index or video file path')
    parser.add_argument('--model', type=str, default='models/weights/yolov8n.pt', help='YOLO weight file path')
    parser.add_argument('--imgsz', type=int, default=640, help='Inference image size')
    parser.add_argument('--conf', type=float, default=0.25, help='Confidence threshold')
    parser.add_argument('--iou', type=float, default=0.45, help='NMS IoU threshold')
    parser.add_argument('--device', type=str, default='', help='Inference device, such as 0, cpu, 0,1')
    parser.add_argument('--max-width', type=int, default=1280, help='Resize display to a maximum width')
    parser.add_argument('--save', type=str, default='', help='Output video path')
    parser.add_argument('--snapshot-dir', type=str, default='results/images', help='Directory for saved snapshots')
    parser.add_argument('--mirror', action='store_true', help='Mirror camera view')
    parser.add_argument('--show-all', action='store_true', help='Show all classes')
    parser.add_argument('--person-only', action='store_true', help='Show only person class')
    args = parser.parse_args()

    if YOLO is None:
        print('Ultralytics is not installed. Run: pip install ultralytics')
        print(f'Import error: {ULTRALYTICS_IMPORT_ERROR}')
        sys.exit(1)

    source = parse_source(args.source)
    cap = open_capture(source)
    if not cap.isOpened():
        print(f'Failed to open input source: {args.source}')
        sys.exit(1)

    if isinstance(source, int):
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    model_path = resolve_model_path(args.model)
    model = YOLO(model_path)

    target_person_only = True
    if args.show_all:
        target_person_only = False
    if args.person_only:
        target_person_only = True

    snapshot_dir = resolve_output_dir(args.snapshot_dir)
    writer = None
    save_path = resolve_output_path(args.save) if args.save else None
    last_snapshot = 'None'
    paused = False
    prev_time = time.time()
    fps = 0.0
    latest_dashboard = None
    events: deque[str] = deque(maxlen=6)
    previous_person_state = False

    source_text = f'Camera {source}' if isinstance(source, int) else f'Video {Path(str(source)).name}'
    device_text = args.device if args.device else 'auto'
    mirror_text = 'ON' if args.mirror else 'OFF'
    display_mode = 'PERSON ONLY' if target_person_only else 'ALL CLASSES'

    settings = {
        'source_text': source_text,
        'model_path': model_path,
        'imgsz': args.imgsz,
        'conf': args.conf,
        'iou': args.iou,
        'device_text': device_text,
        'mirror_text': mirror_text,
        'display_mode': display_mode,
        'save_video': str(save_path) if save_path else '',
        'snapshot_dir': str(snapshot_dir),
    }

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    print('Starting detection. Press Q or ESC to exit.')
    print(f'Using model: {model_path}')
    print('Press P to pause/resume, S to save a snapshot.')
    if save_path is not None:
        print(f'Video will be saved to: {save_path}')

    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                print('Frame read failed. Exiting.')
                break

            if args.mirror and isinstance(source, int):
                frame = cv2.flip(frame, 1)

            frame = resize_keep_aspect(frame, args.max_width)
            results = model.predict(
                source=frame,
                imgsz=args.imgsz,
                conf=args.conf,
                iou=args.iou,
                device=args.device if args.device else None,
                verbose=False,
            )
            result = results[0]
            annotated, person_count, shown_count = annotate_frame(frame, result, target_person_only)

            now = time.time()
            dt = now - prev_time
            prev_time = now
            if dt > 0:
                instant_fps = 1.0 / dt
                fps = instant_fps if fps <= 0 else (0.9 * fps + 0.1 * instant_fps)

            stats = {
                'persons': person_count,
                'shown': shown_count,
                'fps': fps,
            }

            current_person_state = person_count > 0
            if current_person_state and not previous_person_state:
                push_event(events, f'Person detected ({person_count} target(s))')
            elif not current_person_state and previous_person_state:
                push_event(events, 'Target cleared from scene')
            previous_person_state = current_person_state

            latest_dashboard = compose_dashboard(annotated, stats, settings, last_snapshot, str(save_path) if save_path else 'None', events, paused=False)

            if save_path is not None and writer is None:
                h, w = latest_dashboard.shape[:2]
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                writer = cv2.VideoWriter(str(save_path), fourcc, 20.0, (w, h))
                if not writer.isOpened():
                    print(f'Unable to create output video: {save_path}')
                    writer = None
                else:
                    push_event(events, f'Recording started: {save_path.name}')

            if writer is not None:
                writer.write(latest_dashboard)

            cv2.imshow(WINDOW_NAME, latest_dashboard)
        else:
            if latest_dashboard is None:
                blank = np.full((760, 1380, 3), (17, 20, 26), dtype=np.uint8)
                draw_text(blank, 'PAUSED', (620, 380), (255, 255, 255), 1.2, 3)
                cv2.imshow(WINDOW_NAME, blank)
            else:
                paused_view = latest_dashboard.copy()
                overlay = paused_view.copy()
                cv2.rectangle(overlay, (0, 0), (paused_view.shape[1], paused_view.shape[0]), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.18, paused_view, 0.82, 0, paused_view)
                draw_text(paused_view, 'PAUSED', (paused_view.shape[1] // 2 - 80, paused_view.shape[0] // 2), (255, 255, 255), 1.2, 3)
                cv2.imshow(WINDOW_NAME, paused_view)

        key = cv2.waitKey(1 if not paused else 50) & 0xFF
        if key in (ord('q'), 27):
            break
        if key == ord('p'):
            paused = not paused
            push_event(events, 'Paused' if paused else 'Resumed')
            continue
        if key == ord('s') and latest_dashboard is not None:
            snapshot_path = timestamped_output_path(snapshot_dir / 'rescue_snapshot.png', default_suffix='.png')
            cv2.imwrite(str(snapshot_path), latest_dashboard)
            last_snapshot = str(snapshot_path)
            push_event(events, f'Snapshot saved: {snapshot_path.name}')
            print(f'Snapshot saved: {snapshot_path}')

    cap.release()
    if writer is not None:
        writer.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
