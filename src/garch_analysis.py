"""
Функции для расчёта лог-доходностей, оценки GARCH(1,1)
и построения графиков условной волатильности.
"""

from pathlib import Path
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from arch import arch_model


def compute_log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Считает лог-доходности по ценовым рядам и удаляет первые NaN.
    """
    return np.log(prices / prices.shift(1)).dropna()


def fit_garch_and_collect_stats(
    log_returns: pd.DataFrame, run_dir: Path
) -> Tuple[Dict[str, float], Dict[str, pd.Series], Dict[str, pd.Series]]:
    """
    Оценивает GARCH(1,1) по каждому ряду лог-доходностей.

    Возвращает:
    - словарь средних волатильностей по тикерам;
    - словарь рядов условной волатильности;
    - словарь стандартизированных остатков для тестов белошумности.

    По каждому тикеру строится и сохраняется график условной волатильности.
    """
    tickers = log_returns.columns
    volatility_results: Dict[str, float] = {}
    cond_vol_series: Dict[str, pd.Series] = {}
    std_resid_series: Dict[str, pd.Series] = {}

    for ticker in tickers:
        returns = log_returns[ticker].dropna() * 100  # в процентах

        model = arch_model(returns, vol="Garch", p=1, q=1, dist="normal", rescale=False)
        result = model.fit(disp="off")

        # Условная волатильность и среднее значение волатильности
        cond_vol = result.conditional_volatility
        cond_vol.index = returns.index  # для графика сопоставления по датам
        mean_vol = cond_vol.mean()
        volatility_results[ticker] = mean_vol
        cond_vol_series[ticker] = cond_vol

        # Стандартизированные остатки GARCH: нужны для проверки на белошумность
        std_resid = pd.Series(result.std_resid, index=returns.index)
        std_resid_series[ticker] = std_resid

        # График волатильности по каждому банку — сохраняем в output/
        plt.figure(figsize=(10, 4))
        plt.plot(cond_vol)
        plt.title(f"GARCH(1,1) Волатильность: {ticker}")
        plt.ylabel("Волатильность (%)")
        plt.grid(True)
        plt.tight_layout()
        out_path = run_dir / f"волатильность_GARCH_{ticker}.png"
        plt.savefig(out_path)
        plt.close()

    return volatility_results, cond_vol_series, std_resid_series


def plot_volatility_comparison(
    cond_vol_series: Dict[str, pd.Series], run_dir: Path
) -> None:
    """
    Строит общий график для сравнения условной волатильности по всем банкам.
    """
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
    plt.savefig(run_dir / "сравнение_волатильности_GARCH.png")
    plt.close()
    print("  — сопоставление: сравнение_волатильности_GARCH.png")
