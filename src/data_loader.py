"""
Загрузка ценовых рядов акций из Excel.

Выделено в отдельный модуль, чтобы переиспользовать загрузку данных
независимо от анализа волатильности и тестов стационарности.
"""

from pathlib import Path

import pandas as pd

# Пути и настройки источника данных
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
EXCEL_FILENAME = "All shares Ekonometrika.xlsx"
SHEET_NAME = "ALL"

# Анализируемый промежуток по заданию: с 01.09.2014 по настоящий момент
START_DATE = "2014-09-01"


def load_prices() -> pd.DataFrame:
    """
    Загружает цены из Excel, лист ALL, индекс — время.

    Оставляет данные, начиная с 01.09.2014 (по условию задания), сортируя по дате.
    """
    file_path = DATA_DIR / EXCEL_FILENAME
    if not file_path.exists():
        raise FileNotFoundError(
            f"Файл не найден: {file_path}. Положите {EXCEL_FILENAME} в папку data/."
        )

    df = pd.read_excel(file_path, sheet_name=SHEET_NAME)
    df["time"] = pd.to_datetime(df["time"])
    df.set_index("time", inplace=True)

    # Фильтр по заданию: с 01.09.2014 по настоящий момент
    df = df[df.index >= START_DATE].sort_index()
    return df
