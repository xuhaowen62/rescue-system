import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = PROJECT_ROOT / 'configs' / 'app.yaml'
AVAILABLE_MODES = {'detect', 'capture', 'evaluate', 'export'}


def default_settings():
    return {
        'mode': 'detect',
        'source': 0,
        'model': 'models/weights/yolov8n.pt',
        'imgsz': 640,
        'conf': 0.25,
        'iou': 0.45,
        'device': '',
        'save': '',
        'mirror': False,
        'show_all': False,
        'person_only': True,
        'max_width': 1280,
        'out_dir': 'data/raw',
        'save_video': '',
        'prefix': 'capture',
        'data_dir': 'data/test',
        'results_dir': 'results',
        'opset': 17,
        'dynamic': False,
        'simplify': False,
    }


def parse_scalar(value: str):
    text = value.strip()
    lowered = text.lower()
    if lowered in {'true', 'false'}:
        return lowered == 'true'
    if lowered in {'none', 'null', ''}:
        return ''
    try:
        return ast.literal_eval(text)
    except Exception:
        return text.strip("'\"")


def load_simple_config(path: Path) -> dict:
    if not path.exists():
        return default_settings()

    if path.suffix.lower() == '.json':
        with path.open('r', encoding='utf-8') as f:
            data = json.load(f) or {}
        merged = default_settings()
        merged.update(data)
        return merged

    merged = default_settings()
    with path.open('r', encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith('#'):
                continue
            if ':' not in line:
                continue
            key, value = line.split(':', 1)
            merged[key.strip()] = parse_scalar(value)
    return merged


def parse_args():
    parser = argparse.ArgumentParser(description='Rescue system unified entry')
    parser.add_argument('--config', type=str, default=str(DEFAULT_CONFIG), help='Config file path')
    parser.add_argument('--mode', type=str, default='', choices=['', 'detect', 'capture', 'evaluate', 'export'], help='Run mode')
    parser.add_argument('--source', type=str, default='', help='Input source: camera index or video path')
    parser.add_argument('--model', type=str, default='', help='Model weight path')
    parser.add_argument('--imgsz', type=int, default=0, help='Inference image size')
    parser.add_argument('--conf', type=float, default=-1.0, help='Confidence threshold')
    parser.add_argument('--iou', type=float, default=-1.0, help='NMS IoU threshold')
    parser.add_argument('--device', type=str, default='', help='Inference device')
    parser.add_argument('--save', type=str, default='', help='Output video path')
    parser.add_argument('--mirror', action='store_true', help='Mirror the camera view')
    parser.add_argument('--show-all', action='store_true', help='Show all classes')
    parser.add_argument('--person-only', action='store_true', help='Show only person class')
    parser.add_argument('--max-width', type=int, default=0, help='Resize display to a maximum width')
    parser.add_argument('--out-dir', type=str, default='', help='Capture output directory')
    parser.add_argument('--save-video', type=str, default='', help='Capture video output path')
    parser.add_argument('--prefix', type=str, default='', help='Capture filename prefix')
    parser.add_argument('--data-dir', type=str, default='', help='Data directory for evaluation')
    parser.add_argument('--results-dir', type=str, default='', help='Results directory for evaluation')
    parser.add_argument('--opset', type=int, default=0, help='ONNX opset version')
    parser.add_argument('--dynamic', action='store_true', help='Export with dynamic input shape')
    parser.add_argument('--simplify', action='store_true', help='Simplify ONNX graph on export')
    return parser.parse_args()


def merge_settings(cfg: dict, args) -> dict:
    settings = dict(cfg)
    if args.mode:
        settings['mode'] = args.mode
    if args.source:
        settings['source'] = args.source
    if args.model:
        settings['model'] = args.model
    if args.imgsz:
        settings['imgsz'] = args.imgsz
    if args.conf >= 0:
        settings['conf'] = args.conf
    if args.iou >= 0:
        settings['iou'] = args.iou
    if args.device:
        settings['device'] = args.device
    if args.save:
        settings['save'] = args.save
    if args.mirror:
        settings['mirror'] = True
    if args.show_all:
        settings['show_all'] = True
        settings['person_only'] = False
    if args.person_only:
        settings['person_only'] = True
        settings['show_all'] = False
    if args.max_width:
        settings['max_width'] = args.max_width
    if args.out_dir:
        settings['out_dir'] = args.out_dir
    if args.save_video:
        settings['save_video'] = args.save_video
    if args.prefix:
        settings['prefix'] = args.prefix
    if args.data_dir:
        settings['data_dir'] = args.data_dir
    if args.results_dir:
        settings['results_dir'] = args.results_dir
    if args.opset:
        settings['opset'] = args.opset
    if args.dynamic:
        settings['dynamic'] = True
    if args.simplify:
        settings['simplify'] = True

    mode = str(settings.get('mode', 'detect')).strip().lower() or 'detect'
    settings['mode'] = mode if mode in AVAILABLE_MODES else 'detect'

    if settings.get('show_all', False):
        settings['person_only'] = False
    elif settings.get('person_only', False):
        settings['show_all'] = False

    return settings


def ensure_project_dirs():
    folders = [
        PROJECT_ROOT / 'configs',
        PROJECT_ROOT / 'scripts',
        PROJECT_ROOT / 'models' / 'weights',
        PROJECT_ROOT / 'models' / 'exported',
        PROJECT_ROOT / 'data' / 'raw',
        PROJECT_ROOT / 'data' / 'labeled',
        PROJECT_ROOT / 'data' / 'test',
        PROJECT_ROOT / 'results' / 'videos',
        PROJECT_ROOT / 'results' / 'images',
        PROJECT_ROOT / 'results' / 'logs',
        PROJECT_ROOT / 'notebooks',
        PROJECT_ROOT / 'utils',
    ]
    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)


def resolve_path(value: str, default_value: str = '') -> Path:
    raw = str(value).strip() or default_value
    path = Path(raw)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def resolve_model_path(model_value: str) -> str:
    path = resolve_path(model_value, 'models/weights/yolov8n.pt')
    if path.exists():
        return str(path.resolve())
    fallback = PROJECT_ROOT / 'models' / 'weights' / Path(path).name
    return str(fallback.resolve())


def run_script(script_name: str, extra_args: list[str]):
    script = PROJECT_ROOT / script_name
    if not script.exists():
        print(f'Missing script: {script}')
        return 1
    cmd = [sys.executable, str(script), *extra_args]
    print('Running:')
    print(' '.join(cmd))
    return subprocess.call(cmd, cwd=str(PROJECT_ROOT))


def run_detect(settings: dict):
    args = [
        '--source', str(settings.get('source', '0')),
        '--model', resolve_model_path(str(settings.get('model', 'models/weights/yolov8n.pt'))),
        '--imgsz', str(settings.get('imgsz', 640)),
        '--conf', str(settings.get('conf', 0.25)),
        '--iou', str(settings.get('iou', 0.45)),
        '--max-width', str(settings.get('max_width', 1280)),
    ]
    device = str(settings.get('device', '')).strip()
    save = str(settings.get('save', '')).strip()
    if device:
        args += ['--device', device]
    if save:
        args += ['--save', save]
    if settings.get('mirror', False):
        args.append('--mirror')
    if settings.get('show_all', False):
        args.append('--show-all')
    if settings.get('person_only', False):
        args.append('--person-only')
    return run_script('scripts/yolo_detect.py', args)


def run_capture(settings: dict):
    args = [
        '--source', str(settings.get('source', '0')),
        '--out-dir', str(resolve_path(str(settings.get('out_dir', 'data/raw')))),
        '--prefix', str(settings.get('prefix', 'capture')),
        '--max-width', str(settings.get('max_width', 1280)),
    ]
    save_video = str(settings.get('save_video', '')).strip()
    if save_video:
        args += ['--save-video', save_video]
    if settings.get('mirror', False):
        args.append('--mirror')
    return run_script('scripts/data_capture.py', args)


def run_evaluate(settings: dict):
    args = [
        '--data-dir', str(resolve_path(str(settings.get('data_dir', 'data/test')))),
        '--results-dir', str(resolve_path(str(settings.get('results_dir', 'results')))),
    ]
    return run_script('scripts/evaluate.py', args)


def run_export(settings: dict):
    args = [
        '--model', resolve_model_path(str(settings.get('model', 'models/weights/yolov8n.pt'))),
        '--imgsz', str(settings.get('imgsz', 640)),
        '--opset', str(settings.get('opset', 17)),
    ]
    if settings.get('dynamic', False):
        args.append('--dynamic')
    if settings.get('simplify', False):
        args.append('--simplify')
    return run_script('scripts/export_onnx.py', args)


def _enable_ansi_colors() -> bool:
    if not sys.stdout.isatty():
        return False
    if sys.platform != 'win32':
        return True
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)) == 0:
            return False
        new_mode = mode.value | 0x0004
        return kernel32.SetConsoleMode(handle, new_mode) != 0
    except Exception:
        return False


ANSI_ENABLED = _enable_ansi_colors()
RESET = '\x1b[0m'
BOLD = '\x1b[1m'
DIM = '\x1b[2m'
CYAN = '\x1b[36m'
GREEN = '\x1b[32m'
YELLOW = '\x1b[33m'
BLUE = '\x1b[34m'
MAGENTA = '\x1b[35m'
RED = '\x1b[31m'
WHITE = '\x1b[97m'
GRAY = '\x1b[90m'


def color(text: str, code: str) -> str:
    if not ANSI_ENABLED:
        return text
    return f'{code}{text}{RESET}'


def stylize_header(title: str, subtitle: str):
    width = 72
    border = '═' * width
    print()
    print(color(f'╔{border}╗', CYAN))
    title_line = f'  {title}'
    print(color(f'║{title_line.center(width)}║', BOLD + WHITE))
    print(color(f'║{subtitle.center(width)}║', DIM + CYAN))
    print(color(f'╠{border}╣', CYAN))
    print(color('║' + '  说明：本项目仅实现“找到人”模块，不包含后续交互功能。'.ljust(width) + '║', GRAY))
    print(color('║' + '  输出规则：模型导出、图片、视频、截图均采用时间戳命名，不覆盖旧版本。'.ljust(width) + '║', GRAY))
    print(color(f'╚{border}╝', CYAN))


def print_menu_item(key: str, name: str, desc: str, accent: str):
    print(color('  ╭' + '─' * 70 + '╮', GRAY))
    print(color(f'  │ {color(f"[{key}]", accent + BOLD):<8} {color(name, BOLD + WHITE):<18} {color(desc, GRAY)}', ''))
    print(color('  ╰' + '─' * 70 + '╯', GRAY))


def menu_choice():
    stylize_header(
        '基于多模态感知的异构协同搜救系统',
        'Launcher / 主启动器',
    )
    print()
    print(color('  模块总览', BOLD + MAGENTA))
    print_menu_item('1', '人体检测', '启动摄像头/视频人体检测主界面（推荐默认入口）', GREEN)
    print_menu_item('2', '数据采集', '采集图片或录像，用于后续训练与分析', BLUE)
    print_menu_item('3', '模型导出', '导出 ONNX 模型，并自动保留历史版本', YELLOW)
    print_menu_item('4', '结果评估', '查看测试结果或执行评估流程', CYAN)
    print_menu_item('0', '退出启动器', '关闭本程序并返回系统', RED)
    print()
    print(color('  默认入口：直接回车 = 人体检测', GREEN + BOLD))
    print(color('  提示：若使用 PowerShell / PyCharm，终端需支持 ANSI 颜色；不支持时会自动退化为纯文本。', GRAY))
    print()
    choice = input(color('请选择功能编号 [0/1/2/3/4]，直接回车默认进入检测： ', WHITE + BOLD)).strip()
    return choice or '1'


def apply_menu_defaults(choice: str, settings: dict):
    if choice == '1':
        settings['mode'] = 'detect'
    elif choice == '2':
        settings['mode'] = 'capture'
    elif choice == '3':
        settings['mode'] = 'export'
    elif choice == '4':
        settings['mode'] = 'evaluate'
    return settings


def maybe_run_menu(settings: dict) -> int | None:
    if len(sys.argv) > 1:
        return None

    choice = menu_choice()
    if choice == '0':
        print(color('已退出启动器。', GREEN))
        return 0

    if choice not in {'1', '2', '3', '4'}:
        print(color('输入无效，请重新运行后输入 0/1/2/3/4。', RED + BOLD))
        return 1

    settings = apply_menu_defaults(choice, settings)
    mode_labels = {
        'detect': '人体检测',
        'capture': '数据采集',
        'export': '模型导出（ONNX）',
        'evaluate': '结果评估',
    }
    print()
    print(color(f'当前启动模块：{mode_labels[settings["mode"]]}', CYAN + BOLD))
    print(color('正在初始化，请稍候…', DIM + WHITE))
    print()

    runners = {
        'detect': run_detect,
        'capture': run_capture,
        'evaluate': run_evaluate,
        'export': run_export,
    }
    return runners[settings['mode']](settings)
def main():
    args = parse_args()
    ensure_project_dirs()
    cfg = load_simple_config(Path(args.config))
    settings = merge_settings(cfg, args)

    menu_result = maybe_run_menu(settings)
    if menu_result is not None:
        raise SystemExit(menu_result)

    runners = {
        'detect': run_detect,
        'capture': run_capture,
        'evaluate': run_evaluate,
        'export': run_export,
    }
    runner = runners.get(settings['mode'], run_detect)
    raise SystemExit(runner(settings))


if __name__ == '__main__':
    main()
