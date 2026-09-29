from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="day27_dbt_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command="cd /opt/airflow/dags/dbt_project && dbt build --profiles-dir .",
    )
