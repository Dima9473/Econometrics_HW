"""
Утилита для создания папок с результатами вида output/result_N.
"""

from pathlib import Path

# Корень проекта: на одну папку выше src/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

OUTPUT_BASE = PROJECT_ROOT / "output"
RESULT_PREFIX = "result_"


def get_next_result_dir() -> Path:
    """
    Создаёт в output/ новую папку result_N (N = предыдущий максимум + 1)
    и возвращает путь к ней.
    """
    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
    existing = [
        d.name
        for d in OUTPUT_BASE.iterdir()
        if d.is_dir() and d.name.startswith(RESULT_PREFIX)
    ]

    numbers: list[int] = []
    for name in existing:
        suffix = name[len(RESULT_PREFIX) :]
        if suffix.isdigit():
            numbers.append(int(suffix))

    next_num = max(numbers, default=0) + 1
    run_dir = OUTPUT_BASE / f"{RESULT_PREFIX}{next_num}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir
