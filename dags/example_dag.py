"""
Airflow DAG definition — copy this file (and the `tasks/` package) into your Airflow `dags/` folder.

Requires apache-airflow in the deployment environment. Not imported during default local `uv` runs.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from tasks.example import extract, load, transform
from workflows.example_workflow import WORKFLOW

default_args = {
    "owner": WORKFLOW.default_args.get("owner", "airflow"),
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id=WORKFLOW.dag_id,
    description=WORKFLOW.description,
    default_args=default_args,
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["example", "local-dev"],
) as dag:
    extract_task = PythonOperator(task_id="extract", python_callable=extract)
    transform_task = PythonOperator(task_id="transform", python_callable=transform)
    load_task = PythonOperator(task_id="load", python_callable=load)

    extract_task >> transform_task >> load_task
