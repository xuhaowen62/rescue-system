import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from ultralytics import YOLO
except ImportError as exc:
    YOLO = None
    ULTRALYTICS_IMPORT_ERROR = exc
else:
    ULTRALYTICS_IMPORT_ERROR = None

from utils.file_utils import timestamped_output_path


def resolve_model_path(model_value: str) -> Path:
    path = Path(model_value)
    if path.is_absolute() and path.exists():
        return path

    candidates = [
        PROJECT_ROOT / path,
        PROJECT_ROOT / 'models' / 'weights' / path.name,
        Path.cwd() / path,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return PROJECT_ROOT / 'models' / 'weights' / path.name


def main():
    parser = argparse.ArgumentParser(description='导出 YOLO 模型为 ONNX')
    parser.add_argument('--model', type=str, default='models/weights/yolov8n.pt', help='模型权重路径')
    parser.add_argument('--imgsz', type=int, default=640, help='导出尺寸')
    parser.add_argument('--opset', type=int, default=17, help='ONNX opset 版本')
    parser.add_argument('--dynamic', action='store_true', help='动态输入')
    parser.add_argument('--simplify', action='store_true', help='简化 ONNX 图')
    args = parser.parse_args()

    if YOLO is None:
        print('未安装 ultralytics，请先执行：pip install ultralytics')
        print(f'导入错误：{ULTRALYTICS_IMPORT_ERROR}')
        raise SystemExit(1)

    model_path = resolve_model_path(args.model)
    if not model_path.exists():
        print(f'找不到模型文件：{model_path}')
        raise SystemExit(1)

    export_dir = PROJECT_ROOT / 'models' / 'exported'
    export_dir.mkdir(parents=True, exist_ok=True)

    model = YOLO(str(model_path))
    result = model.export(format='onnx', imgsz=args.imgsz, opset=args.opset, dynamic=args.dynamic, simplify=args.simplify)
    print(f'导出结果：{result}')

    result_path = Path(str(result))
    if result_path.exists() and result_path.suffix.lower() == '.onnx':
        timestamped_target = timestamped_output_path(export_dir / f'{result_path.stem}.onnx', default_suffix='.onnx')
        if result_path.resolve() != timestamped_target.resolve():
            timestamped_target.write_bytes(result_path.read_bytes())
            print(f'已保存到：{timestamped_target}')

    print('导出完成。')


if __name__ == '__main__':
    main()