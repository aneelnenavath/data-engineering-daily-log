"""
Day 1 — CSV data cleaner.

Loads a messy customer signup CSV (missing values, exact/near duplicates,
inconsistent text casing), cleans it, and writes:
  - cleaned_customers.csv   the cleaned data
  - fix_log.txt             a plain-English log of every fix that was made

Design choices (the kind of thing an interviewer will ask "why?" about):
  - customer_id, name, email are treated as REQUIRED. A row missing any of
    them is dropped rather than guessed at - you cannot safely invent a
    customer's email address.
  - city, signup_date, plan_type are treated as RECOVERABLE. A missing value
    there is filled with the literal string "unknown" rather than dropping
    the whole row, because we'd rather keep a customer record with one
    unknown field than lose the row entirely.
  - Text normalisation happens BEFORE de-duplication. "London" and "LONDON"
    are the same city, and if we deduplicate first we'll miss that kind of
    near-duplicate.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REQUIRED_FIELDS = ["customer_id", "name", "email"]
RECOVERABLE_FIELDS = ["city", "signup_date", "plan_type"]
TEXT_FIELDS_TO_STRIP = ["name", "email", "city", "signup_date", "plan_type"]


def load(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str)  # dtype=str: don't let pandas guess types yet


def normalise_text(df: pd.DataFrame, log: list[str]) -> pd.DataFrame:
    """Strip stray whitespace and fix inconsistent casing."""
    for col in TEXT_FIELDS_TO_STRIP:
        before = df[col].copy()
        df[col] = df[col].str.strip()
        changed = (before.fillna("") != df[col].fillna("")).sum()
        if changed:
            log.append(f"Stripped leading/trailing whitespace in '{col}' ({changed} cell(s))")

    if "email" in df.columns:
        before = df["email"].copy()
        df["email"] = df["email"].str.lower()
        changed = (before.fillna("") != df["email"].fillna("")).sum()
        if changed:
            log.append(f"Lowercased 'email' for consistent casing ({changed} cell(s))")

    if "city" in df.columns:
        before = df["city"].copy()
        df["city"] = df["city"].str.title()
        changed = (before.fillna("") != df["city"].fillna("")).sum()
        if changed:
            log.append(f"Title-cased 'city' so 'LONDON'/'london'/'London' collapse to one value ({changed} cell(s))")

    if "plan_type" in df.columns:
        before = df["plan_type"].copy()
        df["plan_type"] = df["plan_type"].str.lower()
        changed = (before.fillna("") != df["plan_type"].fillna("")).sum()
        if changed:
            log.append(f"Lowercased 'plan_type' for consistent casing ({changed} cell(s))")

    return df


def drop_missing_required(df: pd.DataFrame, log: list[str]) -> pd.DataFrame:
    before = len(df)
    mask_missing = df[REQUIRED_FIELDS].isna().any(axis=1) | (df[REQUIRED_FIELDS] == "").any(axis=1)
    dropped = df[mask_missing]
    df = df[~mask_missing].copy()
    if len(dropped):
        ids = ", ".join(dropped["customer_id"].astype(str))
        log.append(
            f"Dropped {len(dropped)} row(s) missing a required field {REQUIRED_FIELDS} "
            f"(customer_id(s): {ids})"
        )
    log.append(f"Row count after required-field check: {len(df)} (was {before})")
    return df


def fill_recoverable(df: pd.DataFrame, log: list[str]) -> pd.DataFrame:
    for col in RECOVERABLE_FIELDS:
        missing_mask = df[col].isna() | (df[col] == "")
        n = missing_mask.sum()
        if n:
            df.loc[missing_mask, col] = "unknown"
            log.append(f"Filled {n} missing value(s) in '{col}' with 'unknown'")
    return df


def drop_duplicates(df: pd.DataFrame, log: list[str]) -> pd.DataFrame:
    before = len(df)
    # After normalisation, two rows that are identical in every column but
    # customer_id are the same signup recorded twice - keep the first.
    compare_cols = [c for c in df.columns if c != "customer_id"]
    dup_mask = df.duplicated(subset=compare_cols, keep="first")
    dupes = df[dup_mask]
    df = df[~dup_mask].copy()
    if len(dupes):
        ids = ", ".join(dupes["customer_id"].astype(str))
        log.append(f"Removed {len(dupes)} duplicate row(s) (customer_id(s): {ids})")
    log.append(f"Row count after de-duplication: {len(df)} (was {before})")
    return df


def main() -> None:
    here = Path(__file__).parent
    in_path = here / "messy_customers.csv"
    out_csv = here / "cleaned_customers.csv"
    out_log = here / "fix_log.txt"

    log: list[str] = []
    df = load(in_path)
    log.append(f"Loaded {in_path.name}: {len(df)} rows, {len(df.columns)} columns")

    df = normalise_text(df, log)
    df = drop_missing_required(df, log)
    df = fill_recoverable(df, log)
    df = drop_duplicates(df, log)

    df.to_csv(out_csv, index=False)
    log.append(f"Wrote cleaned data to {out_csv.name}: {len(df)} rows")

    out_log.write_text("\n".join(log) + "\n")

    print("\n".join(log))
    print(f"\nDone. See {out_csv.name} and {out_log.name}.")


if __name__ == "__main__":
    sys.exit(main())
