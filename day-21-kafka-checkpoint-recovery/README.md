# Day 21 — Kafka Checkpoint Recovery

## Objective
Demonstrate that a Kafka consumer, killed mid-stream, can restart and resume
exactly where it left off — no reprocessing, no message loss — using Kafka's
own consumer-group offset commits as the checkpoint mechanism.

## Setup
Reused the Day 19 broker setup (`apache/kafka:latest`, KRaft mode, single
broker) via the same `docker-compose.yml`. A new topic, `day21-events`, was
created with a single partition, since Kafka only guarantees ordering within
one partition and this exercise needed a deterministic sequence to verify
against.

## Approach
The consumer disables auto-commit (`enable_auto_commit=False`) and manually
calls `consumer.commit()` immediately after processing each message, writing
every processed message ID to `processed_log.txt` as it goes. This means the
committed offset in Kafka's internal `__consumer_offsets` topic only ever
advances *after* a message has actually been handled — the checkpoint always
lags reality by at most one message, never ahead of it.

## Simulating a crash
The first two test batches (30 messages each) ran to completion in a single
pass before a manually-timed Ctrl+C could reliably land mid-stream — even
slowed to 1.5 seconds per message, catching the exact right line through a
screenshot-driven workflow proved impractical. Rather than keep trying to
time a Ctrl+C by hand, the consumer script was given a `MAX_MESSAGES`
argument: after processing that many messages in a single run, it calls
`os._exit(1)` — an abrupt process termination with no clean shutdown code
path, deliberately simulating a real crash or `kill -9` rather than a graceful
`.close()`.

## Test
A third batch of 30 messages (ids 61-90) was produced. Running
`python consumer.py 8` processed ids 61 through 68, committing after each,
then hard-crashed on purpose (exit code 1). Restarting with no limit
(`python consumer.py`) resumed at id 69 — not 61 — and ran cleanly through to
90 before timing out with no more messages.

## Verification
`processed_log.txt` was checked programmatically rather than eyeballed: 90
lines total, and a Python check confirmed the sorted, deduplicated set of
IDs matched `range(1, 91)` exactly — no duplicates from reprocessing, no
gaps from lost messages.

## Key takeaway
Kafka consumer groups track progress as committed offsets per
(group_id, topic, partition), stored in the broker's `__consumer_offsets`
topic — not in the consumer process itself. As long as a commit happens only
after the corresponding message is actually processed, a crash at any point
can cost at most reprocessing the *current* message, never losing one that
was already committed. Auto-commit (the default) commits on a timer
regardless of whether processing finished, which can silently lose messages
on a crash; manual commit trades a little throughput for that guarantee.
