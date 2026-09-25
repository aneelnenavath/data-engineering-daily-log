from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import csv
import os

DATA_DIR = "/opt/airflow/data"
CSV_PATH = os.path.join(DATA_DIR, "orders.csv")
FLAG_PATH = os.path.join(DATA_DIR, "transform_attempted.flag")
SUMMARY_PATH = os.path.join(DATA_DIR, "summary.txt")


def extract(**context):
    os.makedirs(DATA_DIR, exist_ok=True)
    # Deterministic synthetic orders so the expected total is known independently.
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["order_id", "amount"])
        for i in range(1, 21):
            writer.writerow([i, 10.0 + i])  # amounts 11.0 .. 30.0
    print(f"Extracted 20 orders to {CSV_PATH}")


def transform(**context):
    # Fail deliberately on the first attempt, succeed on the retry - this proves
    # Airflow's retry mechanism is actually doing something, not just configured.
    if not os.path.exists(FLAG_PATH):
        with open(FLAG_PATH, "w") as f:
            f.write("attempted")
        raise RuntimeError("Simulated transient failure on first attempt")

    total = 0.0
    with open(CSV_PATH, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += float(row["amount"])

    with open(SUMMARY_PATH, "w") as f:
        f.write(f"total_revenue={total}\n")
    print(f"Transform succeeded on retry. Total revenue: {total}")


def load(**context):
    with open(SUMMARY_PATH, "r") as f:
        content = f.read().strip()
    print(f"Loaded final summary: {content}")


default_args = {
    "owner": "anil",
    "retries": 1,
    "retry_delay": timedelta(seconds=10),
}

with DAG(
    dag_id="day22_etl_pipeline",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    extract_task = PythonOperator(task_id="extract", python_callable=extract)
    transform_task = PythonOperator(task_id="transform", python_callable=transform)
    load_task = PythonOperator(task_id="load", python_callable=load)

    extract_task >> transform_task >> load_task
