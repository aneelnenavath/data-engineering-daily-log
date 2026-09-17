# Day 12 — Data Quality Checker

A small, reusable Python script that runs three independent checks against
any CSV and prints a plain-language report, rather than trusting a file
just because it loaded without error.

## Checks

1. **Null rates per column** — count and percentage of missing values,
   surfaced per column rather than one blanket "has nulls" flag.
2. **Duplicate key values** — flags any value in a column that's supposed
   to be a unique key (here, `order_id`) but appears more than once.
3. **Out-of-range numeric values** — flags values outside a given
   min/max for a numeric column (here, `amount` expected between 0 and
   2000).

## Proof it actually catches problems

`orders_quality_sample.csv` has 5 deliberate issues planted in 11 real
rows, so the checker's output could be verified against a known answer
instead of just trusting a clean-looking run:

- Two missing `customer_id` values (rows 4 and 9)
- One missing `amount` value (row 5)
- `order_id = 7` duplicated exactly
- A negative `amount` (-25.00) — a refund miscoded as a sale
- An absurdly high `amount` (9999.99) — a near-certain data-entry error

```bash
python data_quality_checker.py orders_quality_sample.csv
```

All 5 were correctly flagged, nothing else was, confirming the checks
work on real data rather than just on the happy path.

## Usage on any CSV

```python
print_report(
    csv_path="your_file.csv",
    key_col="your_unique_key_column",
    range_col="your_numeric_column",
    min_val=0,
    max_val=2000,
)
```
