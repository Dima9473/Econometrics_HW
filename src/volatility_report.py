"""
Функции для ранжировки по волатильности и формирования текстового отчёта.
"""

from pathlib import Path
from typing import Dict

import pandas as pd

from data_loader import START_DATE


def build_volatility_ranking(volatility_results: Dict[str, float]) -> pd.DataFrame:
    """
    Формирует DataFrame с ранжировкой по средней волатильности и категориями.
    """
    vol_df = pd.DataFrame.from_dict(
        volatility_results, orient="index", columns=["Средняя волатильность (%)"]
    )
    vol_df.sort_values("Средняя волатильность (%)", ascending=False, inplace=True)

    # Категории: низкий, средний, высокий уровень
    quantiles = vol_df["Средняя волатильность (%)"].quantile([0.33, 0.66])
    vol_df["Категория"] = pd.cut(
        vol_df["Средняя волатильность (%)"],
        bins=[-float("inf"), quantiles[0.33], quantiles[0.66], float("inf")],
        labels=["Низкая", "Средняя", "Высокая"],
    )
    return vol_df


def save_and_print_ranking(vol_df: pd.DataFrame, run_dir: Path) -> None:
    """
    Печатает ранжировку в консоль и сохраняет её в CSV.
    """
    print("Ранжировка по средней волатильности (GARCH):")
    print(vol_df)

    csv_path = run_dir / "ранжирование_по_волатильности_GARCH.csv"
    vol_df.to_csv(csv_path, encoding="utf-8-sig")
    print(f"\nРезультаты сохранены в папке: {run_dir}")
    print("  — графики: волатильность_GARCH_<тикер>.png")
    print(f"  — ранжировка: {csv_path.name}")


def write_domain_report(vol_df: pd.DataFrame, run_dir: Path) -> None:
    """
    Формирует текстовый отчёт с комментариями с точки зрения предметной области.
    """
    report_path = run_dir / "отчет_по_волатильности_GARCH.txt"
    high = vol_df[vol_df["Категория"] == "Высокая"].index.tolist()
    mid = vol_df[vol_df["Категория"] == "Средняя"].index.tolist()
    low = vol_df[vol_df["Категория"] == "Низкая"].index.tolist()
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("Комментарий к ранжировке волатильности акций банков РФ\n")
        f.write("(с точки зрения предметной области)\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Период анализа: с {START_DATE} по текущую дату.\n")
        f.write("Модель: GARCH(1,1) по лог-доходностям цен акций.\n\n")
        f.write("Наиболее волатильные банки: " + ", ".join(high) + ".\n")
        f.write(
            "Более высокая волатильность может быть связана с меньшей ликвидностью,\n"
        )
        f.write("размером капитализации, долей розничных инвесторов или спецификой\n")
        f.write("новостного фона (санкции, регуляторные решения).\n\n")
        f.write("Средняя волатильность: " + ", ".join(mid) + ".\n")
        f.write("Наименее волатильные: " + ", ".join(low) + ".\n")
        f.write("Низкая волатильность типична для крупных ликвидных эмитентов\n")
        f.write("и может отражать более стабильные ожидания участников рынка.\n\n")
        f.write("Итоговая ранжировка и числовые значения — в файле ")
        f.write("«ранжирование_по_волатильности_GARCH.csv».\n")
    print(f"  — комментарий: {report_path.name}")
