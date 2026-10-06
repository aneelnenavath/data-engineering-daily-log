# Day 37 — dbt Packages & dbt_utils: Building a Date Dimension Table

## Goal
Every model built so far in this project has been hand-written SQL. Real dbt projects lean heavily
on community packages instead of reinventing common patterns, and dbt_utils is the standard one -
"have you used dbt packages?" is a common interview question. This exercise installs it and uses
two of its macros to build a proper calendar/date dimension table, a classic building block every
BI-style project eventually needs.

## Setup
packages.yml declares dbt-labs/dbt_utils, installed with `dbt deps` into dbt_packages/ (not
committed - package-lock.yml pins the resolved version instead, the same pattern as a
package-lock.json or requirements.txt).

## The model
dim_date.sql uses:
- dbt_utils.date_spine - generates one row per calendar day between two dates, instead of hand-
  writing a recursive CTE or a long UNION of literal dates
- dbt_utils.generate_surrogate_key - builds a hashed, deterministic key from date_day, the same
  pattern used for dimension table keys in real warehouses instead of relying on natural keys

Columns: date_day, date_key (surrogate key), year, month, day_of_month, day_of_week, is_weekend.

## Proof
- Row count, first date, and last date checked directly: 365 rows, 2026-01-01 to 2026-12-31 -
  exactly right for 2026, which is not a leap year.
- First 10 days checked individually against a hand-calculated calendar: every date_day,
  day_of_week, and is_weekend value matched exactly, including Jan 3 (Saturday) and Jan 4 (Sunday)
  both correctly flagged as weekends.

## A small gotcha along the way
dbt show's own preview mechanism appends its own LIMIT to inline queries - writing LIMIT inside the
inline SQL as well caused a parser error. Fixed by removing it from the query and using dbt show's
own --limit flag instead.

## Key takeaway
A date dimension is one of the most common building blocks in dimensional modeling - almost every
fact table eventually needs to join to one for day-of-week, month, or weekend/weekday reporting.
dbt_utils.date_spine turns what would otherwise be error-prone hand-written date generation logic
into a single macro call, and generate_surrogate_key is the standard way to build a dimension
table's primary key from its natural attributes rather than relying on an auto-incrementing id.
Both are exactly the kind of "don't reinvent this" tools a real dbt project reaches for instead of
hand-rolling SQL that a well-tested community package already solves.
