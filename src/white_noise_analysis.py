"""
Функции для проверки белошумности остатков GARCH и их графического анализа.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.stats.diagnostic import acorr_ljungbox


def run_white_noise_tests_for_garch_residuals(
    std_resid_dict: dict[str, pd.Series], run_dir: Path, lag: int = 20
) -> None:
    """
    Проверяет белошумность СТАНДАРТИЗИРОВАННЫХ остатков GARCH-моделей
    с помощью портманто-тестов Бокса–Пирса и Бокса–Льюнга.

    Пояснение по гипотезам:
    - H0: остатки являются белым шумом (нет автокорреляции до заданного лага).
    - H1: остатки не белый шум (есть автокорреляция).

    Если p-значение < 0.05, отвергаем H0 и считаем, что остатки НЕ белый шум.
    """
    results: list[dict[str, float | str | int]] = []

    for ticker, std_resid in std_resid_dict.items():
        series = pd.Series(std_resid).dropna()
        if series.empty:
            continue

        # Тесты Бокса–Пирса и Бокса–Льюнга на один лаг (например, 20)
        ljung_res = acorr_ljungbox(series, lags=[lag], return_df=True, boxpierce=True)
        row = ljung_res.iloc[0]

        results.append(
            {
                "Тикер": ticker,
                "Лаг": lag,
                "Box-Pierce статистика": row["bp_stat"],
                "Box-Pierce p-значение": row["bp_pvalue"],
                "Box-Ljung статистика": row["lb_stat"],
                "Box-Ljung p-значение": row["lb_pvalue"],
                "Вывод (Box-Pierce)": (
                    "Не белый шум (отвергаем H0)"
                    if row["bp_pvalue"] < 0.05
                    else "Белый шум (не отвергаем H0)"
                ),
                "Вывод (Box-Ljung)": (
                    "Не белый шум (отвергаем H0)"
                    if row["lb_pvalue"] < 0.05
                    else "Белый шум (не отвергаем H0)"
                ),
            }
        )

    if not results:
        print("Не удалось выполнить тесты Бокса–Пирса и Бокса–Льюнга: нет остатков GARCH.")
        return

    wn_df = pd.DataFrame(results)
    wn_csv_path = run_dir / "white_noise_tests_garch_residuals.csv"
    wn_df.to_csv(wn_csv_path, encoding="utf-8-sig", index=False)

    print("\nТесты Бокса–Пирса и Бокса–Льюнга для СТАНДАРТИЗИРОВАННЫХ остатков GARCH(1,1):")
    print(wn_df[["Тикер", "Лаг", "Box-Pierce p-значение", "Box-Ljung p-значение"]])
    print(f"\nПолные результаты тестов белошумности сохранены в файле: {wn_csv_path.name}")


def plot_white_noise_diagnostics(std_resid_dict: dict[str, pd.Series], run_dir: Path, max_lag: int = 20) -> None:
    """
    Строит графики для визуальной проверки белошумности стандартизированных остатков GARCH.

    Для каждого тикера сохраняются:
    - график ряда стандартизированных остатков;
    - график ACF (автокорреляционная функция) до max_lag с доверительными интервалами.
    """
    for ticker, std_resid in std_resid_dict.items():
        series = pd.Series(std_resid).dropna()
        if series.empty:
            continue

        # График временного хода стандартизированных остатков
        plt.figure(figsize=(10, 3))
        plt.plot(series.index, series.values, linewidth=0.8)
        plt.axhline(0, color="black", linewidth=1)
        plt.title(f"Стандартизированные остатки GARCH(1,1): {ticker}")
        plt.ylabel("Стандартизированные остатки")
        plt.xlabel("Дата")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        resid_path = run_dir / f"std_resid_garch_{ticker}.png"
        plt.savefig(resid_path)
        plt.close()

        # График автокорреляционной функции (ACF)
        plt.figure(figsize=(8, 3))
        plot_acf(series, lags=max_lag, alpha=0.05)
        plt.title(f"ACF стандартизированных остатков GARCH(1,1): {ticker}")
        plt.tight_layout()
        acf_path = run_dir / f"acf_std_resid_garch_{ticker}.png"
        plt.savefig(acf_path)
        plt.close()

