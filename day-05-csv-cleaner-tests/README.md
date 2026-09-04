# Day 5 — Unit Tests for the Day 1 CSV Cleaner

## What this is

A pytest test suite covering clean_csv.py from Day 1, testing each cleaning
function in isolation against small, hand-built dataframes rather than
running the whole pipeline and eyeballing the result.

## How the import works

clean_csv.py lives in ../day-01-csv-cleaner, not in this folder. The test
file adds that folder to sys.path at import time (using a path built
relative to the test file itself, so it works regardless of where pytest is
run from) rather than duplicating the script here.

## Tests and what each one checks

- test_normalise_text_strips_whitespace_and_fixes_casing — whitespace is
  stripped and casing is normalised (email lowercased, city title-cased,
  plan_type lowercased).
- test_drop_missing_required_removes_row_missing_email — a row missing a
  required field (email) is dropped; a valid row is kept.
- test_drop_missing_required_treats_empty_string_same_as_missing — an empty
  string is treated as missing, not just an actual null value. This is the
  one genuine edge case that could easily be missed: "" and None are not
  the same value in Python, but they should have the same effect here.
- test_fill_recoverable_fills_missing_city_without_dropping_row — a missing
  recoverable field is filled with "unknown" and the row is kept, not
  dropped, confirming the required vs. recoverable distinction actually
  holds in code.
- test_drop_duplicates_removes_same_customer_recorded_twice — two rows
  identical in every column except customer_id collapse to one (keeping
  the first), while a genuinely different row is left alone.

## Result

All 5 tests pass.

## How to run

python -m pytest test_clean_csv.py -v


