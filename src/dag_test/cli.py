from __future__ import annotations

import argparse
import importlib
import json
import sys

from dag_test.runner import WorkflowRunError, run_workflow


def _load_workflow(module_path: str):
    module = importlib.import_module(module_path)
    if not hasattr(module, "WORKFLOW"):
        raise WorkflowRunError(f"Module {module_path!r} must define WORKFLOW")
    return module.WORKFLOW


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run workflow task logic locally (no Airflow scheduler required).",
    )
    parser.add_argument(
        "workflow_module",
        help="Python module path containing WORKFLOW, e.g. workflows.example_workflow",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print task results as JSON",
    )
    args = parser.parse_args(argv)

    try:
        workflow = _load_workflow(args.workflow_module)
        results = run_workflow(workflow)
    except (WorkflowRunError, ImportError, AttributeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        for task_id, value in results.items():
            print(f"{task_id}: {value!r}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
