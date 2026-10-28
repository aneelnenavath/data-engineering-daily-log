# Day 60 — Columnar vs Row Storage: Parquet vs CSV

## Milestone

60 days into this project. Every table built so far has lived either in
Postgres or as plain CSV. Today's question: why does virtually every
production data lake store data in a columnar format like Parquet
instead of row-oriented CSV, and how much does it actually matter in
real, measured numbers rather than as a recited fact.

## The data

generate_data.py wrote 1,000,000 rows across 8 columns (order_id,
customer_id, product_id, warehouse_id, status, amount, shipping_cost,
notes) to both orders.csv and orders.parquet from the identical
DataFrame.

## Proof 1 - file size on disk

    orders.csv:      96 MB
    orders.parquet:  8.6 MB

Parquet's columnar layout lets it compress far more effectively than
CSV - storing all values of one column together, rather than
interleaved with seven other columns' values row by row, exposes much
more repetition and structure for the compressor to exploit. Roughly
11x smaller for the identical data.

## Proof 2 - reading only 2 of 8 columns

compare_column_read.py measured wall-clock time to read just order_id
and amount from each format:

    CSV read (2 of 8 columns):     0.944s
    Parquet read (2 of 8 columns): 0.285s
    Parquet was 3.3x faster

Both produced exactly the same total: 252507200.91. CSV's usecols can
skip building objects for unwanted columns after parsing each row, but
it still has to scan every line of the file, since CSV has no concept
of a column existing separately on disk. Parquet physically stores each
column's data together, so requesting 2 of 8 columns means the other 6
columns' data is never even read off disk.

## Proof 3 - an honest surprise: Parquet still wins even reading everything

Expected the gap to shrink toward parity once column pruning can't help
at all - reading all 8 columns from both formats:

    CSV read (all 8 columns):     1.509s
    Parquet read (all 8 columns): 0.347s
    Parquet was 4.3x faster even reading everything

That wasn't the expected result. Column pruning turned out to be only
part of the story: Parquet's binary encoding means a numeric column is
stored as actual binary numbers, read directly with no parsing, while
CSV stores every value as text that has to be parsed back into a number
on every single read. Parquet's compression also reduces the actual
bytes read from disk even when every column is requested. Column
pruning compounds on top of these two effects rather than being the
only source of the advantage.

## Why this matters

The common framing - "Parquet is faster because it only reads the
columns you need" - is true but incomplete. The full picture, measured
here directly: columnar storage compresses dramatically better (11x
smaller on disk), avoids CSV's per-value text-parsing cost entirely,
and additionally allows skipping whole columns' worth of disk reads
when they aren't needed. All three effects are real and compound
together, which is why the gap didn't close even in the one case
designed specifically to remove the column-pruning advantage.
