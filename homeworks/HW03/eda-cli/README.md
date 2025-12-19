# S03 – eda_cli: мини-EDA для CSV

Небольшое CLI-приложение для базового анализа CSV-файлов.
Используется в рамках Семинара 03 курса «Инженерия ИИ».

## Требования

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) установлен в систему

## Инициализация проекта

В корне проекта (S03):

```bash
uv sync
```

Эта команда:

- создаст виртуальное окружение `.venv`;
- установит зависимости из `pyproject.toml`;
- установит сам проект `eda-cli` в окружение.

## Запуск CLI

### Краткий обзор

```bash
uv run eda-cli overview data/example.csv
```

Параметры:

- `--sep` – разделитель (по умолчанию `,`);
- `--encoding` – кодировка (по умолчанию `utf-8`).

### Полный EDA-отчёт

```bash
uv run eda-cli report data/example.csv --out-dir reports
```

В результате в каталоге `reports/` появятся:

- `report.md` – основной отчёт в Markdown;
- `summary.csv` – таблица по колонкам;
- `missing.csv` – пропуски по колонкам;
- `correlation.csv` – корреляционная матрица (если есть числовые признаки);
- `top_categories/*.csv` – top-k категорий по строковым признакам;
- `hist_*.png` – гистограммы числовых колонок;
- `missing_matrix.png` – визуализация пропусков;
- `correlation_heatmap.png` – тепловая карта корреляций.

## Тесты

```bash
uv run pytest -q
```
### CLI функции:
- `overview` – быстрый обзор датасета;

```bash
uv run eda-cli overview data/example.csv
```

- `report` – полный анализ с графиками и отчетами;

```bash
uv run eda-cli report data/example.csv --out-dir reports
```

### Новые параметры report

- `--title` – заголовок отчёта (# ... в начале report.md);

Даёт отчёту осмысленное имя

- `--top-k-categories` – сколько top-значений выводить для категориальных признаков;

Если уникальных значений много, отчёт становится компактнее и читабельнее

- `--min-missing-share` – порог доли пропусков, выше которого колонка считается проблемной и попадает в отдельный список в отчёте;

Добавляет в report.md новый список-предупреждение.
```bash
uv run eda-cli report data/example.csv \
  --out-dir reports_2024 \
  --title "Весёлый анализ весельчаков" \
  --top-k-categories 3 \
  --min-missing-share 0.1
```