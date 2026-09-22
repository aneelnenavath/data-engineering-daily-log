# Day 19 — Kafka Producer & Consumer (Docker)

A single-broker Kafka setup running in KRaft mode (no separate Zookeeper
container - Kafka now manages its own metadata natively), with a Python
producer sending synthetic order events and a consumer reading them back
and verifying nothing was lost or reordered.

## Three real setup issues along the way

1. **Docker Desktop wasn't running** - the very first `docker compose up`
   failed with `failed to connect to the Docker API`. Simple fix: start
   Docker Desktop and wait for it to fully initialize.
2. **`bitnami/kafka:3.7` doesn't exist on Docker Hub anymore** - Bitnami
   changed its container distribution policy during 2025, moving most
   versioned tags behind a paid "Bitnami Secure Images" subscription and
   leaving only `latest` freely available for many images. Rather than
   depend on an increasingly uncertain third-party image, switched to
   `apache/kafka:latest` - the actual maintainer's own official image,
   which also supports KRaft mode natively.
3. **MSYS path mangling on `kafka-topics.sh`** - the same Git Bash quirk
   from Day 9's HDFS commands. `docker exec kafka /opt/kafka/bin/kafka-topics.sh ...`
   failed because Git Bash rewrote the absolute path into a Windows path
   before Docker ever saw it. Fixed the same way: prefixing with
   `MSYS_NO_PATHCONV=1`.

## Producer (`producer.py`)

Sends 20 synthetic order events (`order_id`, `customer_id`, `amount`,
`timestamp`) to the `orders` topic (1 partition, replication factor 1),
using a fixed random seed for reproducibility.

## Consumer (`consumer.py`)

Reads from the earliest offset and stops once nothing new arrives for 10
seconds - a deliberate one-shot batch read rather than a never-ending
stream, so the script actually finishes for this exercise.

## Verification

All 20 messages were received, at offsets 0-19, in exactly the order
they were produced - order_id 1 at offset 0 through order_id 20 at
offset 19. Kafka guarantees ordering only within a single partition,
which is exactly why this topic was created with 1 partition: with more
partitions, message order across the whole topic wouldn't be
guaranteed, only within each partition. The received order_ids were
checked programmatically against the expected range 1-20 rather than
eyeballed, confirming no message was lost, duplicated, or reordered.
