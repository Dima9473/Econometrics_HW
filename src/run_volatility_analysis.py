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

from adf_analysis import run_adf_for_price_series
from data_loader import load_prices
from garch_analysis import compute_log_returns, fit_garch_and_collect_stats, plot_volatility_comparison
from utils.result_dir import get_next_result_dir
from volatility_report import build_volatility_ranking, save_and_print_ranking, write_domain_report
from white_noise_analysis import plot_white_noise_diagnostics, run_white_noise_tests_for_garch_residuals

warnings.filterwarnings("ignore")




def main():
    # Каждый запуск — новая папка result_N в output/
    run_dir = get_next_result_dir()

    # === Загрузка данных и ADF-тест для ЦЕНОВЫХ рядов ===
    df = load_prices()
    run_adf_for_price_series(df, run_dir)

    # === Расчёт лог-доходностей ===
    log_returns = compute_log_returns(df)

    # === Оценка GARCH(1,1) и сбор статистик ===
    volatility_results, cond_vol_series, std_resid_series = fit_garch_and_collect_stats(
        log_returns, run_dir
    )

    # === Проверка белошумности остатков GARCH(1,1) ===
    run_white_noise_tests_for_garch_residuals(std_resid_series, run_dir, lag=20)
    plot_white_noise_diagnostics(std_resid_series, run_dir, max_lag=20)

    # === Сравнение и ранжировка ===
    vol_df = build_volatility_ranking(volatility_results)
    save_and_print_ranking(vol_df, run_dir)

    # === Сопоставление волатильностей: общий график ===
    plot_volatility_comparison(cond_vol_series, run_dir)

    # === Комментарий с точки зрения предметной области ===
    write_domain_report(vol_df, run_dir)


if __name__ == "__main__":
    main()
