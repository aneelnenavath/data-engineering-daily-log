import sys
from pathlib import Path

import pandas as pd

# clean_csv.py lives in Day 1's folder, not this one, so we point Python at it directly
sys.path.insert(0, str(Path(__file__).parent.parent / "day-01-csv-cleaner"))
import clean_csv


def test_normalise_text_strips_whitespace_and_fixes_casing():
    df = pd.DataFrame({
        "name": [" Alice "],
        "email": ["ALICE@Example.com"],
        "city": ["  london  "],
        "signup_date": ["2024-01-01"],
        "plan_type": ["PRO"],
    })
    log = []

    result = clean_csv.normalise_text(df, log)

    assert result["name"].iloc[0] == "Alice"
    assert result["email"].iloc[0] == "alice@example.com"
    assert result["city"].iloc[0] == "London"
    assert result["plan_type"].iloc[0] == "pro"


def test_drop_missing_required_removes_row_missing_email():
    df = pd.DataFrame({
        "customer_id": ["1", "2"],
        "name": ["Alice", "Bob"],
        "email": ["alice@example.com", None],
        "city": ["London", "Leeds"],
        "signup_date": ["2026-01-01", "2026-01-02"],
        "plan_type": ["premium", "basic"],
    })
    log = []

    result = clean_csv.drop_missing_required(df, log)

    assert len(result) == 1
    assert result["customer_id"].iloc[0] == "1"


def test_drop_missing_required_treats_empty_string_same_as_missing():
    df = pd.DataFrame({
        "customer_id": ["1"],
        "name": ["Alice"],
        "email": [""],
        "city": ["London"],
        "signup_date": ["2026-01-01"],
        "plan_type": ["premium"],
    })
    log = []

    result = clean_csv.drop_missing_required(df, log)

    assert len(result) == 0


def test_fill_recoverable_fills_missing_city_without_dropping_row():
    df = pd.DataFrame({
        "customer_id": ["1"],
        "name": ["Alice"],
        "email": ["alice@example.com"],
        "city": [None],
        "signup_date": ["2026-01-01"],
        "plan_type": ["premium"],
    })
    log = []

    result = clean_csv.fill_recoverable(df, log)

    assert len(result) == 1
    assert result["city"].iloc[0] == "unknown"


def test_drop_duplicates_removes_same_customer_recorded_twice():
    df = pd.DataFrame({
        "customer_id": ["1", "2", "3"],
        "name": ["Alice", "Alice", "Bob"],
        "email": ["alice@example.com", "alice@example.com", "bob@example.com"],
        "city": ["London", "London", "Leeds"],
        "signup_date": ["2026-01-01", "2026-01-01", "2026-01-02"],
        "plan_type": ["premium", "premium", "basic"],
    })
    log = []

    result = clean_csv.drop_duplicates(df, log)

    assert len(result) == 2
    assert set(result["customer_id"]) == {"1", "3"}
