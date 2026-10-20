from __future__ import annotations

from dag_test.runner import TaskSpec, WorkflowSpec
from tasks.example import extract, load, transform

WORKFLOW = WorkflowSpec(
    dag_id="example_etl",
    description="Example ETL workflow for local testing and Airflow deployment",
    default_args={"owner": "data-team"},
    tasks={
        "extract": TaskSpec(task_id="extract", callable=extract, dependencies=()),
        "transform": TaskSpec(
            task_id="transform",
            callable=transform,
            dependencies=("extract",),
        ),
        "load": TaskSpec(task_id="load", callable=load, dependencies=("transform",)),
    },
)
