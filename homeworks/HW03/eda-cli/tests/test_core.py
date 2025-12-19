from __future__ import annotations

import pandas as pd

from eda_cli.core import (
    compute_quality_flags,
    correlation_matrix,
    flatten_summary_for_print,
    missing_table,
    summarize_dataset,
    top_categories,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [10, 20, 30, None],
            "height": [140, 150, 160, 170],
            "city": ["A", "B", "A", None],
        }
    )


def test_summarize_dataset_basic():
    df = _sample_df()
    summary = summarize_dataset(df)

    assert summary.n_rows == 4
    assert summary.n_cols == 3
    assert any(c.name == "age" for c in summary.columns)
    assert any(c.name == "city" for c in summary.columns)

    summary_df = flatten_summary_for_print(summary)
    assert "name" in summary_df.columns
    assert "missing_share" in summary_df.columns


def test_missing_table_and_quality_flags():
    df = _sample_df()
    missing_df = missing_table(df)

    assert "missing_count" in missing_df.columns
    assert missing_df.loc["age", "missing_count"] == 1

    summary = summarize_dataset(df)
    flags = compute_quality_flags(summary, missing_df)
    assert 0.0 <= flags["quality_score"] <= 1.0


def test_correlation_and_top_categories():
    df = _sample_df()
    corr = correlation_matrix(df)
    # корреляция между age и height существует
    assert "age" in corr.columns or corr.empty is False

    top_cats = top_categories(df, max_columns=5, top_k=2)
    assert "city" in top_cats
    city_table = top_cats["city"]
    assert "value" in city_table.columns
    assert len(city_table) <= 2


# проверка флагов качества
def test_compute_quality_flags_new_heuristics():
    """
    Тест новых эвристик в compute_quality_flags.
    Проверяем три сценария:
    1. Константная колонка
    2. ID с дубликатами
    3. Высокая кардинальность категориальных признаков
    """

    # Тест 1: Константная колонка
    df_const = pd.DataFrame({
        "user_id": [1, 2, 3, 4],
        "department": ["IT", "IT", "IT", "IT"],  # Все значения одинаковые
        "salary": [50000, 60000, 70000, 80000],
    })

    summary_const = summarize_dataset(df_const)
    missing_const = missing_table(df_const)
    flags_const = compute_quality_flags(summary_const, missing_const)

    # Проверяем, что флаг has_constant_columns = True
    assert flags_const["has_constant_columns"] is True
    # Проверяем, что список constant_column_names содержит 'department'
    assert "department" in flags_const["constant_column_names"]

    # Тест 2: ID с дубликатами
    df_id_duplicates = pd.DataFrame({
        "user_id": [1, 1, 2, 3],  # Есть дубликаты
        "name": ["Alice", "Bob", "Charlie", "David"],
        "age": [25, 30, 35, 40],
    })

    summary_id = summarize_dataset(df_id_duplicates)
    missing_id = missing_table(df_id_duplicates)
    flags_id = compute_quality_flags(summary_id, missing_id)

    # Проверяем, что флаг has_suspicious_id_duplicates = True
    assert flags_id["has_suspicious_id_duplicates"] is True
    # Проверяем, что список suspicious_id_columns содержит 'user_id'
    assert "user_id" in flags_id["suspicious_id_columns"]

    # Тест 3: Высокая кардинальность категориальных признаков
    # Создаем 150 уникальных значений (порог > 100)
    df_high_card = pd.DataFrame({
        "id": range(150),
        "category": [f"CAT_{i:03d}" for i in range(150)],  # 150 уникальных значений
        "value": [i * 10 for i in range(150)],
    })

    summary_high = summarize_dataset(df_high_card)
    missing_high = missing_table(df_high_card)
    flags_high = compute_quality_flags(summary_high, missing_high)

    # Проверяем, что флаг has_high_cardinality_categoricals = True
    assert flags_high["has_high_cardinality_categoricals"] is True
    # Проверяем, что список high_cardinality_columns содержит 'category'
    assert "category" in flags_high["high_cardinality_columns"]

    # Дополнительная проверка: качество score должно быть меньше 1.0 из-за проблем
    assert flags_const["quality_score"] < 1.0
    assert flags_id["quality_score"] < 1.0
    assert flags_high["quality_score"] < 1.0

    print("Все новые эвристики работают корректно!")


# Еще один тест для проверки полностью пустых колонок
def test_all_missing_columns_flag():
    """Тест для флага has_all_missing_columns"""

    df_all_missing = pd.DataFrame({
        "id": [1, 2, 3, 4],
        "name": ["A", "B", "C", "D"],
        "empty_column": [None, None, None, None],  # Все значения пропущены
    })

    summary = summarize_dataset(df_all_missing)
    missing = missing_table(df_all_missing)
    flags = compute_quality_flags(summary, missing)

    # Проверяем, что флаг has_all_missing_columns = True
    assert flags["has_all_missing_columns"] is True
    # Проверяем, что список all_missing_columns содержит 'empty_column'
    assert "empty_column" in flags["all_missing_columns"]

    print("Флаг has_all_missing_columns работает корректно!")