# Econometrics_HW — анализ волатильности акций банков РФ

Расчёт условной волатильности (GARCH), ранжировка банков и сохранение результатов в папку `output/result_N`.

## Требования

- Python 3.10+
- Файл с данными: **All shares Ekonometrika.xlsx** (лист «ALL»)

## Установка

1. Клонируйте репозиторий и перейдите в каталог проекта:

   ```bash
   cd Econometrics_HW
   ```

2. Создайте виртуальное окружение (рекомендуется):

   ```bash
   python -m venv .venv
   ```

   Активация:
   - Windows (cmd): `.venv\Scripts\activate.bat`
   - Windows (PowerShell): `.venv\Scripts\Activate.ps1`
   - Windows (bash): `source .venv/Scripts/activate`
   - Linux/macOS: `source .venv/bin/activate`

3. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

4. Положите файл **All shares Ekonometrika.xlsx** в папку **data/**:

   ```text
   Econometrics_HW/
   └── data/
       └── All shares Ekonometrika.xlsx
   ```

## Запуск

Из корня проекта выполните:

```bash
python src/run_volatility_analysis.py
```

Скрипт:

- загружает данные из `data/All shares Ekonometrika.xlsx` (лист «ALL»);
- считает лог-доходности и оценивает GARCH(1,1) по каждому тикеру;
- строит графики волатильности и сохраняет результаты в новую папку **output/result_N** (при каждом запуске N увеличивается: result_1, result_2, …).

В папке запуска будут:

- `volatility_<тикер>.png` — графики условной волатильности по банкам;
- `volatility_comparison.png` — сопоставление волатильностей;
- `volatility_ranking.csv` — ранжировка и категории (низкая / средняя / высокая);
- `volatility_report.txt` — краткий комментарий по результатам.
