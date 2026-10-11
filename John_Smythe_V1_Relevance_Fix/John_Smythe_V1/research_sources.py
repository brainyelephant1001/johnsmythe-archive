
"""
JOHN SMYTHE RESEARCH ENGINE
Official Research Sources — Version 0.1

You ask. We investigate. You decide.

A central register of public research sources.

This module does not automatically retrieve records.
It identifies official sources and creates search links.

Source authenticity does not automatically establish
the truth of every statement in a document.
"""

from urllib.parse import quote_plus


OFFICIAL_SOURCES = [
    {
        "id": "parliament",
        "name": "UK Parliament",
        "domain": "parliament.uk",
        "homepage": "https://www.parliament.uk/",
        "category": "Parliamentary records",
        "description": (
            "Parliamentary questions, debates, "
            "committees and voting records."
        ),
    },
    {
        "id": "government",
        "name": "UK Government",
        "domain": "gov.uk",
        "homepage": "https://www.gov.uk/",
        "category": "Government publications",
        "description": (
            "Government policies, announcements, "
            "consultations and departmental publications."
        ),
    },
    {
        "id": "legislation",
        "name": "UK Legislation",
        "domain": "legislation.gov.uk",
        "homepage": "https://www.legislation.gov.uk/",
        "category": "Legislation",
        "description": (
            "Acts of Parliament, statutory instruments "
            "and legislative changes."
        ),
    },
    {
        "id": "statistics",
        "name": "Office for National Statistics",
        "domain": "ons.gov.uk",
        "homepage": "https://www.ons.gov.uk/",
        "category": "Official statistics",
        "description": (
            "Population, employment, economic "
            "and social statistics."
        ),
    },
    {
        "id": "archives",
        "name": "The National Archives",
        "domain": "nationalarchives.gov.uk",
        "homepage": "https://www.nationalarchives.gov.uk/",
        "category": "Historical records",
        "description": (
            "Archived government records and "
            "historical public documents."
        ),
    },
    {
        "id": "manifestos",
        "name": "Political Manifestos",
        "domain": None,
        "homepage": None,
        "category": "Election commitments",
        "description": (
            "Party manifestos from different elections. "
            "Individual documents must be sourced "
            "and checked before comparison."
        ),
    },
]


def list_sources():
    """Return the official research source register."""

    return [
        dict(source)
        for source in OFFICIAL_SOURCES
    ]


def get_source(source_id):
    """Find a source by its identifier."""

    for source in OFFICIAL_SOURCES:
        if source["id"] == source_id:
            return dict(source)

    return None


def search_link(source_id, question):
    """Create a web search link restricted to a source."""

    source = get_source(source_id)

    if not source:
        return None

    domain = source.get("domain")

    if not domain:
        return None

    question = str(question).strip()

    if not question:
        return None

    query = f"site:{domain} {question}"

    return (
        "https://www.google.com/search?q="
        + quote_plus(query)
    )


def source_search_plan(question):
    """Prepare search links for registered sources."""

    searches = []

    for source in OFFICIAL_SOURCES:

        link = search_link(
            source["id"],
            question
        )

        if not link:
            continue

        searches.append({
            "source_id": source["id"],
            "source_name": source["name"],
            "category": source["category"],
            "search_url": link,
            "retrieval_status": "Not retrieved",
            "verified": False,
        })

    return {
        "question": str(question).strip(),
        "sources": searches,
        "source_count": len(searches),
        "note": (
            "These are search links, not retrieved "
            "or independently verified evidence."
        ),
    }


if __name__ == "__main__":

    print("=" * 55)
    print("JOHN SMYTHE — OFFICIAL RESEARCH SOURCES")
    print("=" * 55)

    question = input(
        "\nEnter a research question:\n> "
    )

    plan = source_search_plan(question)

    print("\nResearch sources:")

    for source in plan["sources"]:
        print(
            "\n" + source["source_name"]
            + "\n" + source["search_url"]
        )

    print("\nSources available:", plan["source_count"])
