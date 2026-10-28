# Day 59 — Idempotent File Ingestion via Checksums

## What this demonstrates

A pipeline that reads a file from an inbox and processes it has no
inherent way to know whether it's seeing a genuinely new file or the
same file arriving again - an orchestrator retry after a timeout, an
upstream system redelivering after a transient failure, or the same
content arriving under a brand new filename. Row-level idempotency
(Day 47's upserts) and record-level deduplication (Day 53) solve
related but different problems; this is about the file itself: making
sure the same file's content is never processed twice, no matter how
many times - or under how many names - it shows up.

## Proof 1 - a naive pipeline silently double-counts on a retry

naive_ingest.py reads a CSV, sums its revenue, and appends the result to
a persistent ledger - standing in for a real downstream database write.

Ran once against incoming_orders.csv (5 rows, true revenue 478.59), then
ran again against the identical file, simulating an orchestrator retry.
Both runs succeeded with no error and no warning. The ledger ended up
with:

    incoming_orders.csv: 5 rows, revenue 478.59
    incoming_orders.csv: 5 rows, revenue 478.59

The same file counted twice - 957.18 instead of the true 478.59 - with
nothing in either run's output suggesting anything had gone wrong.

## Proof 2 - a checksum manifest catches the retry regardless of filename

idempotent_ingest.py computes a SHA-256 hash of each file's actual
bytes before doing anything else, checks it against a JSON manifest of
every checksum already processed, and only reads/sums/ledgers the file
if the checksum is new.

    First run (incoming_orders.csv):
      Processed incoming_orders.csv: 5 rows, revenue 478.59 (checksum recorded)

    Second run, identical file:
      SKIPPED: incoming_orders.csv was already processed - not reprocessing.

    Third run, same content copied to a brand new filename
    (incoming_orders_resend_v2.csv):
      SKIPPED: incoming_orders_resend_v2.csv was already processed as
      part of run 'incoming_orders.csv' - not reprocessing.

Because the check is based on the file's content hash rather than its
name, a redelivery under a completely different filename - which is
exactly how many real-world redeliveries actually arrive, with a new
timestamp or suffix - was still caught and skipped correctly.

## Proof 3 - genuinely new content still processes normally

A real second batch of orders (incoming_orders_day2.csv, 3 different
rows, true revenue 483.15) has a different checksum and was processed
normally:

    Processed incoming_orders_day2.csv: 3 rows, revenue 483.15 (checksum recorded)

The final ledger holds exactly two entries, no duplicates, totalling
the correct 478.59 + 483.15 = 961.74 - proving the checksum check isn't
blocking legitimate new data, only genuine repeats.

## Why this matters

Retries are a normal, expected part of running pipelines - timeouts,
transient failures, and at-least-once delivery guarantees all mean a
file can legitimately arrive or be processed more than once. A pipeline
that can't tell a retry from new data will silently corrupt downstream
totals every time one happens, with no error to catch it. Checking a
content hash against a manifest before processing turns that silent
corruption into a safe no-op, and doing it by content rather than
filename means the protection survives the file being renamed along the
way, which is exactly how most real redeliveries show up.
