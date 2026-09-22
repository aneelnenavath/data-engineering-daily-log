# Day 17 — Star Schema Design

A dimensional model for the same e-commerce order data used throughout
this project, designed for analytical queries rather than transactional
ones. The diagram lives in `star_schema.md` (GitHub renders Mermaid
natively inside `.md` files).

## Fact vs. dimension, and why the grain matters

`fact_orders` sits at the center, holding one row per order and only the
numeric measures (`quantity`, `unit_price`, `total_amount`) plus foreign
keys pointing out to each dimension. Nothing descriptive lives in the
fact table itself — no customer name, no product category — because the
fact table's whole job is to be small, numeric, and fast to scan over
millions of rows. Deciding the **grain** (what one fact row represents —
here, one order) is the first and most important decision in any star
schema; every measure and every dimension key has to agree with it.

## Four dimensions, chosen deliberately

- `dim_customer`, `dim_product` — the two obvious ones, holding
  everything descriptive about who bought and what was bought.
- `dim_date` — close to mandatory in a real star schema. Storing a
  `date_key` instead of a raw date lets a warehouse pre-compute
  `day_of_week`, `quarter`, and `year` once per calendar day rather than
  recomputing them in every query — exactly what would have made Day
  13's rolling-revenue and month-over-month queries cheaper at scale.
- `dim_payment_method` — a smaller, realistic fourth dimension, showing
  that a dimension doesn't need to be large or central to earn its own
  table; it just needs to be a distinct descriptive attribute of the
  fact.

## How this connects to earlier days

This is the third time this project has faced the same underlying
choice — normalize or denormalize — and answered it differently on
purpose, depending on the workload:

- **Day 7 (MySQL, OLTP)**: normalized into 5 tables to minimize
  redundancy and keep writes cheap and consistent.
- **Day 11 (Cassandra)**: denormalized into two query-specific tables
  (`orders_by_customer`, `orders_by_product`), because Cassandra has no
  JOIN and rows must already be shaped for the one query each table
  answers.
- **Day 17 (star schema)**: denormalizes each *dimension* into one wide
  table (e.g. `dim_product` holds `category` and `subcategory` directly
  rather than in separate normalized tables), while still using foreign
  keys and joins between the fact and its dimensions — a deliberate
  middle ground between Day 7's full normalization and Day 11's
  complete denormalization, optimized specifically for the kind of
  aggregate-and-group-by queries Days 13-16 were practicing.
