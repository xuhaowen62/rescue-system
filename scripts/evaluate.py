import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def count_files(folder: Path, patterns):
    total = 0
    for pattern in patterns:
        total += len(list(folder.rglob(pattern)))
    return total


def main():
    parser = argparse.ArgumentParser(description='搜救系统数据/结果检查')
    parser.add_argument('--data-dir', type=str, default='data/test', help='数据目录')
    parser.add_argument('--results-dir', type=str, default='results', help='结果目录')
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not data_dir.is_absolute():
        data_dir = PROJECT_ROOT / data_dir

    results_dir = Path(args.results_dir)
    if not results_dir.is_absolute():
        results_dir = PROJECT_ROOT / results_dir

    image_count = count_files(data_dir, ['*.jpg', '*.jpeg', '*.png', '*.bmp']) if data_dir.exists() else 0
    label_count = count_files(PROJECT_ROOT / 'data' / 'labeled', ['*.txt']) if (PROJECT_ROOT / 'data' / 'labeled').exists() else 0
    video_count = count_files(results_dir / 'videos', ['*.mp4', '*.avi', '*.mov']) if (results_dir / 'videos').exists() else 0
    image_result_count = count_files(results_dir / 'images', ['*.jpg', '*.jpeg', '*.png', '*.bmp']) if (results_dir / 'images').exists() else 0

    print('=== 目录检查 ===')
    print(f'数据目录：{data_dir}')
    print(f'结果目录：{results_dir}')
    print(f'测试图片数量：{image_count}')
    print(f'标注文件数量：{label_count}')
    print(f'结果视频数量：{video_count}')
    print(f'结果图片数量：{image_result_count}')
    print('说明：该脚本用于项目检查与数据统计，不计算模型精度指标。')


if __name__ == '__main__':
    main()
