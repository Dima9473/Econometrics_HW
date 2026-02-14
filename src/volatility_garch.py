"""
Анализ волатильности цен акций крупнейших банков РФ.
Построение GARCH-моделей, расчёт условной волатильности, ранжировка
(наиболее / средне / наименее волатильные) и комментарий с точки зрения
предметной области.
Период: с 01.09.2014 по текущую дату (по заданию).
Данные: data/All shares Ekonometrika.xlsx, лист "ALL".
Результаты: при каждом запуске создаётся output/result_N (графики, CSV, отчёт).
"""
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from arch import arch_model

warnings.filterwarnings("ignore")

# Пути: данные в data/, результаты в output/result_1, output/result_2, ...
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_BASE = PROJECT_ROOT / "output"
RESULT_PREFIX = "result_"


def get_next_result_dir():
    """Создаёт в output/ новую папку result_N (N = предыдущий максимум + 1)."""
    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
    existing = [d.name for d in OUTPUT_BASE.iterdir() if d.is_dir() and d.name.startswith(RESULT_PREFIX)]
    numbers = []
    for name in existing:
        suffix = name[len(RESULT_PREFIX) :]
        if suffix.isdigit():
            numbers.append(int(suffix))
    next_num = max(numbers, default=0) + 1
    run_dir = OUTPUT_BASE / f"{RESULT_PREFIX}{next_num}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir

EXCEL_FILENAME = "All shares Ekonometrika.xlsx"
SHEET_NAME = "ALL"

# Анализируемый промежуток по заданию: с 01.09.2014 по настоящий момент
START_DATE = "2014-09-01"


def load_prices():
    """Загружает цены из Excel, лист ALL, индекс — время. Оставляет данные с 01.09.2014."""
    file_path = DATA_DIR / EXCEL_FILENAME
    if not file_path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}. Положите {EXCEL_FILENAME} в папку data/.")
    df = pd.read_excel(file_path, sheet_name=SHEET_NAME)
    df["time"] = pd.to_datetime(df["time"])
    df.set_index("time", inplace=True)
    # Фильтр по заданию: с 01.09.2014 по настоящий момент
    df = df[df.index >= START_DATE].sort_index()
    return df


def main():
    # Каждый запуск — новая папка result_N в output/
    run_dir = get_next_result_dir()

    # === Загрузка данных ===
    df = load_prices()

    # === Расчёт лог-доходностей ===
    log_returns = np.log(df / df.shift(1)).dropna()
    tickers = log_returns.columns
    volatility_results = {}

    # === Расчёт волатильности через GARCH(1,1) ===
    # GARCH(1,1) — стандартная модель для условной волатильности; хорошо
    # описывает кластеризацию волатильности и часто достаточна для рядов доходностей.
    # При необходимости можно подобрать порядок по AIC (см. дополнительно в отчёте).
    cond_vol_series = {}
    for ticker in tickers:
        returns = log_returns[ticker].dropna() * 100  # в процентах

        model = arch_model(returns, vol="Garch", p=1, q=1, dist="normal", rescale=False)
        result = model.fit(disp="off")

        cond_vol = result.conditional_volatility
        cond_vol.index = returns.index  # для графика сопоставления по датам
        mean_vol = cond_vol.mean()
        volatility_results[ticker] = mean_vol
        cond_vol_series[ticker] = cond_vol

        # График волатильности по каждому банку — сохраняем в output/
        plt.figure(figsize=(10, 4))
        plt.plot(cond_vol)
        plt.title(f"GARCH(1,1) Волатильность: {ticker}")
        plt.ylabel("Волатильность (%)")
        plt.grid(True)
        plt.tight_layout()
        out_path = run_dir / f"volatility_{ticker}.png"
        plt.savefig(out_path)
        plt.close()

    # === Сравнение и ранжировка ===
    vol_df = pd.DataFrame.from_dict(
        volatility_results, orient="index", columns=["Средняя волатильность (%)"]
    )
    vol_df.sort_values("Средняя волатильность (%)", ascending=False, inplace=True)

    # === Категории: низкий, средний, высокий уровень ===
    quantiles = vol_df["Средняя волатильность (%)"].quantile([0.33, 0.66])
    vol_df["Категория"] = pd.cut(
        vol_df["Средняя волатильность (%)"],
        bins=[-np.inf, quantiles[0.33], quantiles[0.66], np.inf],
        labels=["Низкая", "Средняя", "Высокая"],
    )

    # === Вывод результатов ===
    print("Ранжировка по средней волатильности (GARCH):")
    print(vol_df)

    # === Сохранение в CSV в папку текущего запуска ===
    csv_path = run_dir / "volatility_ranking.csv"
    vol_df.to_csv(csv_path, encoding="utf-8-sig")
    print(f"\nРезультаты сохранены: {run_dir}")
    print("  — графики: volatility_<тикер>.png")
    print(f"  — ранжировка: {csv_path.name}")

    # === Сопоставление волатильностей: общий график для сравнения банков ===
    vol_compare = pd.DataFrame(cond_vol_series)
    plt.figure(figsize=(12, 5))
    for col in vol_compare.columns:
        plt.plot(vol_compare.index, vol_compare[col], label=col, alpha=0.8)
    plt.title("Сопоставление условной волатильности (GARCH) по банкам")
    plt.ylabel("Волатильность (%)")
    plt.xlabel("Дата")
    plt.legend(loc="best", fontsize=9)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(run_dir / "volatility_comparison.png")
    plt.close()
    print("  — сопоставление: volatility_comparison.png")

    # === Комментарий с точки зрения предметной области ===
    report_path = run_dir / "volatility_report.txt"
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
        f.write("Более высокая волатильность может быть связана с меньшей ликвидностью,\n")
        f.write("размером капитализации, долей розничных инвесторов или спецификой\n")
        f.write("новостного фона (санкции, регуляторные решения).\n\n")
        f.write("Средняя волатильность: " + ", ".join(mid) + ".\n")
        f.write("Наименее волатильные: " + ", ".join(low) + ".\n")
        f.write("Низкая волатильность типична для крупных ликвидных эмитентов\n")
        f.write("и может отражать более стабильные ожидания участников рынка.\n\n")
        f.write("Итоговая ранжировка и числовые значения — в файле volatility_ranking.csv.\n")
    print(f"  — комментарий: {report_path.name}")


if __name__ == "__main__":
    main()
