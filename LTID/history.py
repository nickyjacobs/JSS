"""Historical threat data storage and retrieval."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

HISTORY_DIR = Path(__file__).parent / "data" / "history"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def get_history_file(date: datetime | None = None) -> Path:
    """Get history file path for a date (default: today)."""
    if date is None:
        date = datetime.utcnow()
    return HISTORY_DIR / f"threats_{date.strftime('%Y-%m-%d')}.json"


class ThreatHistory:
    """Manages historical threat data storage."""

    def save_snapshot(self, data: dict[str, Any]) -> None:
        """Save a snapshot of current threat data."""
        try:
            snapshot = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "total_threats": data.get("aggregate", {}).get("total_threats", 0),
                "by_source": data.get("aggregate", {}).get("by_source", {}),
                "by_country": data.get("aggregate", {}).get("by_country", {}),
                "by_type": data.get("aggregate", {}).get("by_type", {}),
                "top_countries": data.get("aggregate", {}).get("metrics", {}).get("top_countries", [])[:10],
            }
            history_file = get_history_file()
            # Load existing data for today
            if history_file.exists():
                with open(history_file) as f:
                    daily_data = json.load(f)
            else:
                daily_data = {"snapshots": []}
            daily_data["snapshots"].append(snapshot)
            # Keep only last 24 snapshots (hourly for a day)
            daily_data["snapshots"] = daily_data["snapshots"][-24:]
            with open(history_file, "w") as f:
                json.dump(daily_data, f, indent=2)
        except Exception as e:
            logger.error("Failed to save history snapshot: %s", e)

    def get_timeline(self, days: int = 7) -> list[dict[str, Any]]:
        """Get timeline data for the last N days."""
        timeline = []
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=i)
            history_file = get_history_file(date)
            if history_file.exists():
                try:
                    with open(history_file) as f:
                        daily_data = json.load(f)
                    snapshots = daily_data.get("snapshots", [])
                    if snapshots:
                        # Get last snapshot of the day
                        last = snapshots[-1]
                        timeline.append({
                            "date": date.strftime("%Y-%m-%d"),
                            "total": last.get("total_threats", 0),
                            "by_source": last.get("by_source", {}),
                        })
                except Exception as e:
                    logger.error("Failed to load history for %s: %s", date, e)
        return sorted(timeline, key=lambda x: x["date"])

    def get_country_trends(self, days: int = 7) -> dict[str, list[tuple[str, int]]]:
        """Get country trends over time."""
        trends: dict[str, list[tuple[str, int]]] = {}
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=i)
            history_file = get_history_file(date)
            if history_file.exists():
                try:
                    with open(history_file) as f:
                        daily_data = json.load(f)
                    snapshots = daily_data.get("snapshots", [])
                    if snapshots:
                        last = snapshots[-1]
                        top_countries = last.get("top_countries", [])
                        for country, count in top_countries[:5]:
                            if country not in trends:
                                trends[country] = []
                            trends[country].append((date.strftime("%Y-%m-%d"), count))
                except Exception:
                    pass
        return trends
