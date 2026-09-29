from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowException
from datetime import datetime
import re


def verify_counts(**context):
    produced_raw = context["ti"].xcom_pull(task_ids="produce_events")
    consumed_raw = context["ti"].xcom_pull(task_ids="consume_events")

    produced_match = re.search(r"PRODUCED_COUNT=(\d+)", str(produced_raw))
    consumed_match = re.search(r"CONSUMED_COUNT=(\d+)", str(consumed_raw))

    if not produced_match or not consumed_match:
        raise AirflowException(
            f"Could not parse counts. produced_raw={produced_raw!r}, consumed_raw={consumed_raw!r}"
        )

    produced = int(produced_match.group(1))
    consumed = int(consumed_match.group(1))
    print(f"Produced: {produced}, Consumed: {consumed}")

    if produced != consumed:
        raise AirflowException(f"MISMATCH: produced {produced} but consumed {consumed}")

    print("VERIFIED: produced count matches consumed count exactly.")


with DAG(
    dag_id="day25_kafka_orchestration",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:

    produce_events = BashOperator(
        task_id="produce_events",
        bash_command="python /opt/airflow/dags/scripts/produce_events.py",
    )

    consume_events = BashOperator(
        task_id="consume_events",
        bash_command="python /opt/airflow/dags/scripts/bounded_consume.py",
    )

    verify_task = PythonOperator(
        task_id="verify_counts",
        python_callable=verify_counts,
    )

    produce_events >> consume_events >> verify_task
