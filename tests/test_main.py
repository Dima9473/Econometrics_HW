"""
Тесты для модуля src.main.
"""
import pytest
from pathlib import Path

# Корень проекта
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def test_data_dir_exists():
    """Каталог data должен существовать."""
    assert DATA_DIR.is_dir()


def test_excel_data_exists():
    """В data должен быть файл с данными."""
    xlsx = DATA_DIR / "All shares Ekonometrika.xlsx"
    assert xlsx.exists(), "Ожидается файл All shares Ekonometrika.xlsx в data/"
