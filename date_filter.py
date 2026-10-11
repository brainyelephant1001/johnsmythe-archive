
"""
JOHN SMYTHE RESEARCH ENGINE
Date Filtering Module - Version 0.2

Recognises simple year ranges in research questions.

Separates records into:
- Within the requested date range
- Outside the requested date range
- Missing or invalid dates

Original evidence records are not modified.
"""

import re
from datetime import datetime


def extract_date_range(question):
    """Identify a simple year range in a research question."""

    question = str(question)

    match = re.search(
        r"\b(?:since|from)\s+((?:19|20)\d{2})\b",
        question,
        re.IGNORECASE,
    )

    if match:
        return {
            "start_year": int(match.group(1)),
            "end_year": None,
        }

    match = re.search(
        r"\bbetween\s+((?:19|20)\d{2})\s+and\s+((?:19|20)\d{2})\b",
        question,
        re.IGNORECASE,
    )

    if match:
        return {
            "start_year": int(match.group(1)),
            "end_year": int(match.group(2)),
        }

    return None


def classify_records_by_date(records, date_range):
    """
    Separate records by publication date.

    Returns a dictionary containing matching,
    excluded, and undated records.
    """

    matching = []
    excluded = []
    undated = []

    if date_range is None:
        return {
            "matching": list(records),
            "excluded": [],
            "undated": [],
        }

    start_year = date_range["start_year"]
    end_year = date_range["end_year"]

    for record in records:
        if not isinstance(record, dict):
            continue

        raw_date = record.get("date") or record.get("release_date")

        if not raw_date:
            undated.append(record)
            continue

        try:
            year = datetime.fromisoformat(
                str(raw_date).replace("Z", "+00:00")
            ).year
        except (ValueError, TypeError):
            undated.append(record)
            continue

        if year < start_year:
            excluded.append(record)
        elif end_year is not None and year > end_year:
            excluded.append(record)
        else:
            matching.append(record)

    return {
        "matching": matching,
        "excluded": excluded,
        "undated": undated,
    }


def filter_records_by_date(records, date_range):
    """Return only records within the requested range."""

    classification = classify_records_by_date(
        records,
        date_range,
    )

    return classification["matching"]


if __name__ == "__main__":
    question = (
        "What action has the UK Parliament taken "
        "to address homelessness since 2020?"
    )

    sample_records = [
        {"title": "Old guidance", "date": "2017-01-12"},
        {"title": "Recent policy", "date": "2022-06-15"},
        {"title": "New report", "date": "2026-09-30"},
        {"title": "Undated evidence", "date": ""},
    ]

    date_range = extract_date_range(question)

    results = classify_records_by_date(
        sample_records,
        date_range,
    )

    print("Date range:", date_range)
    print("Matching:", len(results["matching"]))
    print("Excluded:", len(results["excluded"]))
    print("Undated:", len(results["undated"]))

    for record in results["matching"]:
        print(record["date"], "-", record["title"])
