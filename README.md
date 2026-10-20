# dag-test

This repo is for building Airflow DAGs and testing their logic on your machine before you deploy them. It uses [uv](https://docs.astral.sh/uv/) to manage the Python environment. You won't need a fully armed and operational Airflow instance on your laptop—just write the tasks, run them in order locally, and when everything looks good, copy the same code into your real setup when you're ready to join the fleet.

There is a small example pipeline (extract → transform → load) in `workflows/example_workflow.py` and `dags/example_dag.py` if you want something to copy from. Consider it your training run on Yavin before the real mission.

## How the repo is organized

- **`tasks/`** — Where the actual work happens: plain Python functions for extract, transform, load, and so on. These are easy to unit test and are what your Airflow operators will call later.
- **`workflows/`** — Defines a `WORKFLOW`: each task’s id, which function runs it, and what it depends on. Think of it as the briefing before the run—the graph you use locally.
- **`dags/`** — Airflow-facing files: `DAG` objects and `PythonOperator` wiring that match the workflow. When you are ready for production, these are what you copy into Airflow’s `dags` folder.
- **`src/dag_test/`** — A tiny local runner and CLI. It walks dependencies in order (upstream/downstream)—no hyperspace shortcuts, just the route you actually filed—without pretending to be Airflow itself.
- **`tests/`** — Pytest tests for your tasks and the runner. Trust the local run, but verify here.

## What you need first

You will need Python 3.11 or newer and [uv](https://docs.astral.sh/uv/getting-started/installation/) on your PATH. If you do not have uv yet, the usual install is:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Using WSL (Windows)

If you develop on Windows with [WSL](https://learn.microsoft.com/en-us/windows/wsl/), treat WSL as your Linux machine for this project. Run `uv`, `pytest`, and all the commands in this README from a WSL terminal (Ubuntu, Debian, etc.), not from PowerShell or Command Prompt, unless you have deliberately set up the same tooling on Windows itself.

**Where to put the repo.** Clone or copy the project into the Linux filesystem when you can, for example under `~/projects/dagTest`. Paths like `/home/you/projects/dagTest` work well with `uv` and `.venv`. If the repo lives on the Windows drive (`/mnt/c/Users/...`), installs and tests usually still work, but they can be slower—long stretches on a desert highway, if you know the type—and some setups also warn about hardlinks when creating the virtual environment. If you see that, you can run:

```bash
export UV_LINK_MODE=copy
uv sync --extra dev
```

**Paths in commands.** Use Linux-style paths in `cd` and in your editor. For example:

```bash
cd ~/projects/dagTest
uv sync --extra dev
```

instead of `C:\Users\...`.

**Editor.** If you use VS Code or Cursor, open the folder *in WSL* (Remote – WSL / “Open Folder in WSL”) so the integrated terminal and Python tools use the same environment as your WSL shell. You want your IDE and terminal on the same side of the blast doors.

**First-time WSL packages.** Most dependencies install from prebuilt wheels. If something fails to build, install basic build tools in your distro, then retry `uv sync`:

```bash
sudo apt update && sudo apt install -y build-essential python3-dev
```

After that, the rest of this README applies the same way as on any other Linux machine.

## Getting set up

Clone or open the project, then from the repo root:

```bash
cd /path/to/dagTest
uv sync --extra dev
```

That command creates a virtual environment in `.venv/` (which git ignores) and installs this project in editable mode, including pytest for tests.

If you also want to import or sanity-check Airflow DAG files on your laptop, you can pull in Airflow as an optional extra. The install is fairly large—more battle station than snub fighter:

```bash
uv sync --extra dev --extra airflow
```

## Running a workflow locally

To run every task in the example workflow, in dependency order, without Airflow:

```bash
uv run dag-test workflows.example_workflow
```

You should see something like:

```text
extract: {'rows': [...]}
transform: {'row_count': 2, 'total_value': 30}
load: 'loaded 2 rows, total_value=30'
```

If the output looks right, you're allowed to say you have a good feeling about this. If not, check the dependency chain before you punch it.

If you prefer JSON (for scripts or piping elsewhere), add `--json`:

```bash
uv run dag-test workflows.example_workflow --json
```

The same entry point works as a module if you like that better:

```bash
uv run python -m dag_test.cli workflows.example_workflow
```

## Running tests

```bash
uv run pytest
```

Do or do not run the suite before you push—either way, the CI droids will remember.

## Adding your own DAG

There is another path… well, really just this one:

1. Put your task functions in something like `tasks/your_dag.py`. If a task needs output from an earlier step, accept `upstream_results` and/or `**context` the way `tasks/example.py` does.
2. Describe the graph in `workflows/your_workflow.py` as a `WORKFLOW` built from `TaskSpec` and `WorkflowSpec` in `dag_test.runner`.
3. Try it locally: `uv run dag-test workflows.your_workflow`
4. Add tests under `tests/` for the task functions, and optionally a test that calls `run_workflow(WORKFLOW)` end to end.
5. Add `dags/your_dag.py` with `PythonOperator` tasks and the same dependency chain as in `WORKFLOW`.

Try to keep real business logic in `tasks/` and keep each file under `dags/` thin—mostly operators, schedule, and defaults—so moving to Airflow is mostly copy-and-wire rather than rewriting logic. Size matters not; look at `example_dag.py` you must.

## Moving code to Airflow

When local runs and tests pass, you're cleared for the approach:

1. Copy `dags/your_dag.py` into your Airflow project (or sync the repo). Bring along the `tasks/` package, and `workflows/` too if the DAG imports `WORKFLOW` for metadata.
2. Make sure workers can import those modules—either add the project root to `PYTHONPATH` or install the package in the Airflow environment.
3. On the Airflow side, install `apache-airflow` and whatever libraries your tasks need (that can be separate from this dev venv).
4. Turn the DAG on in the UI and run or backfill as you normally would.

`dags/example_dag.py` targets Airflow 2.x (`apache-airflow>=2.10,<3` if you use the optional `airflow` extra here).

## Git and what not to commit

The `.gitignore` keeps local tooling out of the repo: `.venv/` from `uv sync`, `.uv/` cache/metadata in the project, plus usual Python bytecode, build output, and common IDE clutter.

You should commit your source and `uv.lock` (created the first time you run `uv sync`) so everyone gets the same dependency versions—frozen, reproducible, the kind of intel a whole alliance could use. Do not commit `.venv/`.

## Commands you will use often

- `uv sync --extra dev` — install or refresh dependencies
- `uv run dag-test workflows.example_workflow` — run the example workflow locally
- `uv run pytest` — run the test suite
- `uv add <package>` — add a library your tasks need at runtime
- `uv sync --extra airflow` — optional; only if you want Airflow available locally for DAG import checks

May the fork be with you.
