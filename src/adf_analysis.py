"""
Функции для проверки сходимости (стационарности) ценовых рядов
с помощью расширенного теста Дики–Фуллера и их графического отображения.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.tsa.stattools import adfuller


def run_adf_for_price_series(df: pd.DataFrame, run_dir: Path, alpha: float = 0.05) -> None:
    """
    Выполняет расширенный тест Дики–Фуллера (ADF) для КАЖДОГО ценового ряда.

    По результатам теста для каждого тикера делается вывод о стационарности
    ценового ряда, формируется таблица и сохраняется в CSV в папку текущего запуска.
    Дополнительно для КАЖДОГО ценового ряда строится график с подписью
    параметров ADF-теста (ADF-статистика, p-значение, вывод).

    Пояснение по гипотезам теста Дики–Фуллера:
    - Н0: В ряду есть единичный корень (ряд НЕстационарен).
    - Н1: Ряд стационарен.

    Если p-значение < alpha (по умолчанию 0.05), то нулевая гипотеза
    отвергается и ряд можно считать стационарным.
    """
    results: list[dict[str, float | str | int]] = []

    for col in df.columns:
        series = df[col].dropna()

        # Пропускаем полностью пустые ряды, чтобы не ломать анализ.
        if series.empty:
            continue

        # Используем autolag="AIC", чтобы автоматически подобрать число лагов.
        adf_res = adfuller(series, autolag="AIC")
        stat, p_value, used_lag, n_obs, crit_vals, ic_best = adf_res

        is_stationary = p_value < alpha
        conclusion = "Стационарен (отвергаем H0)" if is_stationary else "Не стационарен (не отвергаем H0)"

        # Графическое представление сходимости (стационарности) ценового ряда
        plt.figure(figsize=(10, 3))
        plt.plot(series.index, series.values)
        plt.title(
            f"Ценовой ряд {col}\nADF={stat:.3f}, p-value={p_value:.3g}, {conclusion}"
        )
        plt.ylabel("Цена")
        plt.xlabel("Дата")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        fig_path = run_dir / f"price_series_adf_{col}.png"
        plt.savefig(fig_path)
        plt.close()

        results.append(
            {
                "Ряд": col,
                "ADF статистика": stat,
                "p-значение": p_value,
                "Использовано лагов": used_lag,
                "Число наблюдений": n_obs,
                "Критическое значение 1%": crit_vals["1%"],
                "Критическое значение 5%": crit_vals["5%"],
                "Критическое значение 10%": crit_vals["10%"],
                "Информационный критерий (AIC)": ic_best,
                "Вывод": conclusion,
            }
        )

    if not results:
        print("Не удалось выполнить ADF-тест: нет непустых ценовых рядов.")
        return

    adf_df = pd.DataFrame(results)

    # Сохраняем подробные результаты теста в CSV
    adf_csv_path = run_dir / "adf_price_series_results.csv"
    adf_df.to_csv(adf_csv_path, encoding="utf-8-sig", index=False)

    # В консоль выводим краткий итог по каждому ряду.
    print("\nРезультаты расширенного теста Дики–Фуллера для ЦЕНОВЫХ рядов:")
    print(adf_df[["Ряд", "ADF статистика", "p-значение", "Вывод"]])
    print(f"\nПолные результаты ADF-теста сохранены в файле: {adf_csv_path.name}")

