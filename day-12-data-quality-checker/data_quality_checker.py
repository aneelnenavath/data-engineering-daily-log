"""
Data quality checker.

Runs three independent checks against a CSV and prints a plain-language
report:
  1. Null rates per column
  2. Duplicate values in a column that's supposed to be a unique key
  3. Out-of-range numeric values (below a min or above a max)

Usage:
    python data_quality_checker.py <csv_path>
"""

import sys
import pandas as pd


def check_null_rates(df: pd.DataFrame) -> dict:
    """Return {column: (null_count, null_rate_pct)} for every column with at least one null."""
    results = {}
    total = len(df)
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        if null_count > 0:
            results[col] = (null_count, round(100 * null_count / total, 1))
    return results


def check_duplicate_keys(df: pd.DataFrame, key_col: str) -> pd.DataFrame:
    """Return the rows whose key_col value appears more than once."""
    dupes_mask = df[key_col].duplicated(keep=False)
    return df[dupes_mask]


def check_out_of_range(df: pd.DataFrame, col: str, min_val: float, max_val: float) -> pd.DataFrame:
    """Return rows where col is outside [min_val, max_val], ignoring nulls (handled separately)."""
    numeric = pd.to_numeric(df[col], errors="coerce")
    out_of_range_mask = numeric.notna() & ((numeric < min_val) | (numeric > max_val))
    return df[out_of_range_mask]


def print_report(csv_path: str, key_col: str, range_col: str, min_val: float, max_val: float) -> None:
    df = pd.read_csv(csv_path)
    print(f"Data quality report for: {csv_path}")
    print(f"Total rows: {len(df)}")
    print("=" * 60)

    print("\n[1] Null rates by column")
    nulls = check_null_rates(df)
    if not nulls:
        print("  No nulls found in any column.")
    else:
        for col, (count, pct) in nulls.items():
            print(f"  {col}: {count} nulls ({pct}% of rows)")

    print(f"\n[2] Duplicate '{key_col}' values (should be a unique key)")
    dupes = check_duplicate_keys(df, key_col)
    if dupes.empty:
        print(f"  No duplicate {key_col} values found.")
    else:
        dupe_keys = sorted(dupes[key_col].unique())
        print(f"  Found {len(dupes)} rows sharing {len(dupe_keys)} duplicated {key_col} value(s): {dupe_keys}")
        print(dupes.to_string(index=False))

    print(f"\n[3] Out-of-range '{range_col}' values (expected {min_val}-{max_val})")
    bad_range = check_out_of_range(df, range_col, min_val, max_val)
    if bad_range.empty:
        print(f"  All {range_col} values are within range.")
    else:
        print(f"  Found {len(bad_range)} row(s) outside the expected range:")
        print(bad_range.to_string(index=False))

    print("\n" + "=" * 60)
    print("Report complete.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python data_quality_checker.py <csv_path>")
        sys.exit(1)

    print_report(
        csv_path=sys.argv[1],
        key_col="order_id",
        range_col="amount",
        min_val=0,
        max_val=2000,
    )
