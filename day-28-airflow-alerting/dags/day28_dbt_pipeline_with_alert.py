from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.email import send_email


def alert_on_failure(context):
    ti = context["task_instance"]
    subject = f"[Airflow] {ti.dag_id}.{ti.task_id} failed"
    body = (
        f"<p>Task <b>{ti.task_id}</b> in DAG <b>{ti.dag_id}</b> failed.</p>"
        f"<p>Run ID: {context['run_id']}</p>"
        f"<p>Execution date: {context['logical_date']}</p>"
        f"<p>Log URL: {ti.log_url}</p>"
    )
    send_email(to="anil@example.com", subject=subject, html_content=body)


with DAG(
    dag_id="day28_dbt_pipeline_with_alert",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command="cd /opt/airflow/dags/dbt_project && dbt build --profiles-dir .",
        on_failure_callback=alert_on_failure,
    )
