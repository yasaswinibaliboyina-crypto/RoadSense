
import json
from datetime import datetime, timezone
from pathlib import Path

HISTORY_FILE = (
    Path(__file__).resolve().parent / "road_report_history.json"
)


def save_local_report(report: dict) -> dict:
    """Append a road-risk report to local JSON history."""
    try:
        if HISTORY_FILE.exists():
            with HISTORY_FILE.open("r", encoding="utf-8") as file:
                reports = json.load(file)
        else:
            reports = []

        if not isinstance(reports, list):
            reports = []

        entry = {
            "report_id": datetime.now(timezone.utc).strftime(
                "%Y%m%dT%H%M%S%fZ"
            ),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "report": report,
        }

        reports.append(entry)

        with HISTORY_FILE.open("w", encoding="utf-8") as file:
            json.dump(reports, file, indent=2)

        return {
            "saved": True,
            "mode": "local",
            "report_id": entry["report_id"],
            "total_reports": len(reports),
        }

    except (OSError, json.JSONDecodeError) as exc:
        return {
            "saved": False,
            "mode": "local",
            "message": str(exc),
        }


def get_local_reports() -> list:
    """Return saved reports, newest first."""
    if not HISTORY_FILE.exists():
        return []

    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as file:
            reports = json.load(file)

        if not isinstance(reports, list):
            return []

        return list(reversed(reports))

    except (OSError, json.JSONDecodeError):
        return []
