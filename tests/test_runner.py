from dag_test.runner import run_workflow
from workflows.example_workflow import WORKFLOW


def test_run_example_workflow_end_to_end():
    results = run_workflow(WORKFLOW)
    assert set(results) == {"extract", "transform", "load"}
    assert "loaded 2 rows" in results["load"]
