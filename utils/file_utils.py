from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Union

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PathLike = Union[str, Path]


def resolve_project_path(value: PathLike, default: str = '', project_root: Path = PROJECT_ROOT) -> Path:
    raw = str(value).strip() or default
    path = Path(raw)
    if not path.is_absolute():
        path = project_root / path
    return path


def timestamp_token(moment: datetime | None = None) -> str:
    moment = moment or datetime.now()
    return moment.strftime('%Y%m%d_%H%M%S_%f')


def timestamped_file_path(path_value: PathLike, default_suffix: str = '', moment: datetime | None = None) -> Path:
    path = Path(path_value)
    if default_suffix and not path.suffix:
        path = path.with_suffix(default_suffix)

    stamp = timestamp_token(moment)
    candidate = path.with_name(f'{path.stem}_{stamp}{path.suffix}')
    candidate.parent.mkdir(parents=True, exist_ok=True)

    index = 1
    while candidate.exists():
        candidate = path.with_name(f'{path.stem}_{stamp}_{index}{path.suffix}')
        index += 1

    return candidate


def timestamped_output_path(path_value: PathLike, default_suffix: str = '', moment: datetime | None = None) -> Path:
    return timestamped_file_path(path_value, default_suffix=default_suffix, moment=moment)