from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.sensors.filesystem import FileSensor
from datetime import datetime
import csv
import os

INCOMING_PATH = "/opt/airflow/data/incoming/orders.csv"
GOOD_SUMMARY_PATH = "/opt/airflow/data/processed_summary.txt"
QUARANTINE_PATH = "/opt/airflow/data/quarantine_report.txt"


def check_quality(**context):
    bad_rows = []
    with open(INCOMING_PATH, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            amount_raw = row["amount"].strip()
            if amount_raw == "" or float(amount_raw) < 0:
                bad_rows.append(row["order_id"])
    if bad_rows:
        context["ti"].xcom_push(key="bad_rows", value=bad_rows)
        return "quarantine_bad_data"
    return "process_good_data"


def process_good_data(**context):
    total = 0.0
    with open(INCOMING_PATH, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += float(row["amount"])
    with open(GOOD_SUMMARY_PATH, "w") as f:
        f.write(f"total_revenue={total}\n")
    print(f"Processed clean data. Total revenue: {total}")


def quarantine_bad_data(**context):
    bad_rows = context["ti"].xcom_pull(key="bad_rows", task_ids="check_quality")
    with open(QUARANTINE_PATH, "w") as f:
        f.write(f"bad_order_ids={bad_rows}\n")
    print(f"Quarantined bad rows: {bad_rows}")


def finish(**context):
    print("Pipeline finished.")


with DAG(
    dag_id="day23_conditional_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    wait_for_file = FileSensor(
        task_id="wait_for_file",
        fs_conn_id="fs_default",
        filepath=INCOMING_PATH,
        poke_interval=5,
        timeout=120,
    )

    check_quality_task = BranchPythonOperator(
        task_id="check_quality",
        python_callable=check_quality,
    )

    process_good_data_task = PythonOperator(
        task_id="process_good_data",
        python_callable=process_good_data,
    )

    quarantine_bad_data_task = PythonOperator(
        task_id="quarantine_bad_data",
        python_callable=quarantine_bad_data,
    )

    finish_task = PythonOperator(
        task_id="finish",
        python_callable=finish,
        trigger_rule="none_failed_min_one_success",
    )

    wait_for_file >> check_quality_task >> [process_good_data_task, quarantine_bad_data_task] >> finish_task
