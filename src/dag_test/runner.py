from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable


TaskCallable = Callable[..., Any]


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    callable: TaskCallable
    dependencies: tuple[str, ...] = ()


@dataclass
class WorkflowSpec:
    dag_id: str
    description: str
    tasks: dict[str, TaskSpec]
    default_args: dict[str, Any] = field(default_factory=dict)


class WorkflowRunError(Exception):
    pass


def _topological_order(tasks: dict[str, TaskSpec]) -> list[str]:
    in_degree = {task_id: 0 for task_id in tasks}
    adjacency: dict[str, list[str]] = {task_id: [] for task_id in tasks}

    for task_id, spec in tasks.items():
        for dep in spec.dependencies:
            if dep not in tasks:
                raise WorkflowRunError(f"Task {task_id!r} depends on unknown task {dep!r}")
            adjacency[dep].append(task_id)
            in_degree[task_id] += 1

    queue: deque[str] = deque(sorted(tid for tid, deg in in_degree.items() if deg == 0))
    order: list[str] = []

    while queue:
        current = queue.popleft()
        order.append(current)
        for neighbor in sorted(adjacency[current]):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(tasks):
        raise WorkflowRunError("Workflow contains a cyclic dependency")

    return order


def run_workflow(workflow: WorkflowSpec, *, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Execute task callables in dependency order, mirroring Airflow's upstream/downstream graph.

    Returns a mapping of task_id -> return value from each callable.
    """
    ctx = dict(context or {})
    ctx.setdefault("dag_id", workflow.dag_id)
    ctx.update(workflow.default_args)

    results: dict[str, Any] = {}
    for task_id in _topological_order(workflow.tasks):
        spec = workflow.tasks[task_id]
        task_context = {**ctx, "task_id": task_id, "upstream_results": dict(results)}
        results[task_id] = spec.callable(**task_context)

    return results
