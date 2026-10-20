from __future__ import annotations

from typing import Any


def extract(**context: Any) -> dict[str, Any]:
    """Pull raw data (stand in for DB/API extract in Airflow)."""
    return {"rows": [{"id": 1, "value": 10}, {"id": 2, "value": 20}]}


def transform(*, upstream_results: dict[str, Any], **context: Any) -> dict[str, Any]:
    """Transform data using upstream task output."""
    payload = upstream_results["extract"]
    total = sum(row["value"] for row in payload["rows"])
    return {"row_count": len(payload["rows"]), "total_value": total}


def load(*, upstream_results: dict[str, Any], **context: Any) -> str:
    """Load transformed data (stand in for warehouse load)."""
    summary = upstream_results["transform"]
    return f"loaded {summary['row_count']} rows, total_value={summary['total_value']}"
