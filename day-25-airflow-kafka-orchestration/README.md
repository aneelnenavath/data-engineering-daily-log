# Day 25 — Airflow Orchestrating Kafka via BashOperator

## Objective
Have Airflow actually orchestrate an external Kafka producer/consumer
pipeline via `BashOperator` - the same pattern real pipelines use to kick
off a Spark job or a dbt run - with the DAG verifying its own correctness
by comparing produced and consumed message counts and failing itself on a
mismatch, rather than relying on an external check afterward.

## Setup: two independently-run containers, one shared network
Kafka (`apache/kafka:latest`, KRaft mode) and Airflow (`apache/airflow:2.9.3`
standalone) were started as two separate `docker run` containers, joined to
a user-defined network (`docker network create daylog-net`) so they could
resolve each other by container name. Kafka's advertised listener was set
to `kafka:9092` rather than `localhost:9092`, since only containers on that
network needed to reach it this time. `kafka-python` was installed inside
the Airflow container, hitting Airflow's own broken bare `pip` (a virtualenv
quirk, not the Anaconda issue from Day 13) - fixed the same way, with
`python -m pip install kafka-python`.

## DAG design
`day25_kafka_orchestration` has three tasks: `produce_events` (BashOperator)
sends 25 known messages, `consume_events` (BashOperator) runs a bounded
consumer that stops once 15 seconds pass with no new message, and
`verify_counts` (PythonOperator) parses both tasks' printed output via XCom
and raises an `AirflowException` - failing the DAG itself - if the produced
and consumed counts don't match.

## The real bug: a silent, exception-free failure
The first run's `produce_events` and `consume_events` both reported success,
but `verify_counts` failed with `produced 25 but consumed 0`. Running the
consumer script directly, outside Airflow entirely, reproduced the same
zero - ruling out any Airflow-specific cause. A diagnostic script checking
`consumer.assignment()` after an explicit `poll()` showed an empty set: the
consumer never received any partition assignment at all, with no exception
raised anywhere in the visible code path. Enabling kafka-python's internal
DEBUG logging (redirected to a file - and correcting for the fact that a
`>` redirect on a `docker exec` command lands on the host, not inside the
container) revealed the real cause: every `FindCoordinatorRequest` came
back with `error_code=15` (`COORDINATOR_NOT_AVAILABLE`), retried
indefinitely and failing only via a silent internal timeout.

Error 15 on a single-broker cluster is a well-known Kafka gotcha: the
internal `__consumer_offsets` topic, which every consumer group depends on,
defaults to `offsets.topic.replication.factor=3`. A single broker can never
satisfy that, so the topic is never created, and every consumer group's
coordinator lookup fails forever - silently, since produce and non-group
consume operations are entirely unaffected and still look completely
healthy. The fix was recreating the Kafka container with
`KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1` explicitly set.

## Verification
After the fix, the diagnostic script's `consumer.assignment()` returned a
real partition immediately. Re-triggering the full DAG produced a genuine
success, and the `verify_counts` task's own log confirmed
`Produced: 25, Consumed: 25` with an explicit `VERIFIED` line - the DAG's
built-in self-check, not an assumption drawn from a green run.

## Key takeaway
This was the most consequential bug of the whole Streaming & Orchestration
stretch: a failure with zero exceptions anywhere in application code,
indistinguishable from a working setup unless you specifically checked
partition assignment or turned on protocol-level debug logging. It's also
a reminder that a single-broker Kafka cluster needs several defaults
adjusted to behave like a real cluster of one - `offsets.topic.replication.
factor=1` chief among them - and that "no error" is never the same claim
as "working correctly."
