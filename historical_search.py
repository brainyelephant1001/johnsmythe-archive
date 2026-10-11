
"""
JOHN SMYTHE RESEARCH ENGINE
Historical Search — Version 0.1

Identifies historical periods in research questions
and filters dated public records.

This module does not retrieve historical records.
It prepares date filters for source-specific searches.
"""

import re
from datetime import date, datetime


def extract_date_range(question):
    """Identify a historical date range from a question."""

    text = str(question).lower()

    years = [
        int(year)
        for year in re.findall(
            r"\b(?:19|20)\d{2}\b",
            text
        )
    ]

    years = list(dict.fromkeys(years))

    current_year = date.today().year

    start_year = None
    end_year = None

    if len(years) >= 2:
        start_year = min(years)
        end_year = max(years)

    elif len(years) == 1:
        year = years[0]

        if re.search(r"\b(since|from|after)\b", text):
            start_year = year
            end_year = current_year

        elif re.search(r"\b(before|until|up to)\b", text):
            end_year = year

        else:
            start_year = year
            end_year = year

    return {
        "start_year": start_year,
        "end_year": end_year,
        "years_mentioned": years,
        "has_date_filter": bool(years),
    }


def parse_record_date(value):
    """Parse a public-record date into a date object."""

    if not value:
        return None

    try:
        return datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        ).date()

    except (TypeError, ValueError):
        return None


def filter_records_by_date(records, date_range):
    """Keep records falling within the requested years."""

    start_year = date_range.get("start_year")
    end_year = date_range.get("end_year")

    if start_year is None and end_year is None:
        return list(records)

    filtered = []

    for record in records:
        record_date = parse_record_date(
            record.get("date")
        )

        if record_date is None:
            continue

        if start_year is not None:
            if record_date.year < start_year:
                continue

        if end_year is not None:
            if record_date.year > end_year:
                continue

        filtered.append(record)

    return filtered


def historical_search_plan(question):
    """Generate the historical search parameters."""

    date_range = extract_date_range(question)

    return {
        "question": question,
        "date_range": date_range,
        "requires_historical_search": (
            date_range["has_date_filter"]
        ),
        "note": (
            "Historical date filtering must be applied "
            "to appropriately retrieved source records."
        ),
    }


if __name__ == "__main__":

    print("JOHN SMYTHE — HISTORICAL SEARCH")

    question = input(
        "\nEnter a historical research question:\n> "
    )

    plan = historical_search_plan(question)

    print("\nHistorical search plan:")
    print(plan)
