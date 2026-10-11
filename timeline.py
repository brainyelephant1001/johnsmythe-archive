
"""
JOHN SMYTHE RESEARCH ENGINE
Research Timeline — Version 0.1

Organises discovered evidence chronologically.

Features:
- Date parsing
- Oldest-to-newest or newest-to-oldest ordering
- Year grouping
- Timeline statistics
- Unverified evidence labels

Does not independently verify source accuracy.
"""

from datetime import datetime
from collections import defaultdict


def parse_date(value):
    """Convert a date string into a datetime object."""

    if not value:
        return None

    try:
        return datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )
    except (ValueError, TypeError):
        return None


def build_timeline(records, newest_first=False):
    """Create a chronological timeline of research records."""

    events = []

    for record in records:

        if not isinstance(record, dict):
            continue

        raw_date = record.get("date")
        parsed = parse_date(raw_date)

        if parsed is None:
            continue

        events.append({
            "date": parsed.date().isoformat(),
            "year": parsed.year,
            "title": record.get("title", "Untitled record"),
            "source": record.get("source", "Unknown source"),
            "reference": record.get("reference"),
            "url": record.get("url"),
            "question": record.get("question"),
            "answer": record.get("answer"),
            "verified": False,
        })

    events.sort(
        key=lambda event: event["date"],
        reverse=newest_first
    )

    return events


def group_by_year(events):
    """Group timeline events by year."""

    groups = defaultdict(list)

    for event in events:
        groups[event["year"]].append(event)

    return dict(sorted(groups.items()))


def timeline_statistics(events):
    """Produce basic timeline statistics."""

    if not events:
        return {
            "total_events": 0,
            "earliest": None,
            "latest": None,
            "years_covered": [],
        }

    dates = sorted(event["date"] for event in events)

    return {
        "total_events": len(events),
        "earliest": dates[0],
        "latest": dates[-1],
        "years_covered": sorted({
            event["year"] for event in events
        }),
    }


if __name__ == "__main__":

    print("JOHN SMYTHE — RESEARCH TIMELINE")

    sample_records = [
        {
            "title": "Example parliamentary record",
            "date": "2020-03-15",
            "source": "UK Parliament",
            "reference": "EXAMPLE-001",
        },
        {
            "title": "Second example record",
            "date": "2015-06-10",
            "source": "UK Parliament",
            "reference": "EXAMPLE-002",
        },
    ]

    events = build_timeline(sample_records)

    print("\nTimeline events:")

    for event in events:
        print(
            event["date"],
            "-",
            event["title"]
        )

    print("\nStatistics:")
    print(timeline_statistics(events))
