
"""
JOHN SMYTHE RESEARCH ENGINE
Local Web Server - Version 0.6

You ask. We investigate. You decide.

Combines:
- Parliamentary questions
- GOV.UK publications
- Legislation search results
- ONS statistics search results
- Relevance assessments
- Date filtering
- Chronological research timeline

All retrieved records remain unverified evidence leads.
"""

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter
from datetime import datetime, timezone

from flask import Flask, jsonify, request, send_file

from analysis import ResearchAnalysis
from sourcecheck import SourceCheck
from app import search_parliament
from relevance import rank_evidence
from evidence_assessment_v02 import assess_record
from timeline import (
    build_timeline,
    group_by_year,
    timeline_statistics,
)
from date_filter import (
    extract_date_range,
    classify_records_by_date,
)
from research_sources import source_search_plan
from government_research import search_government
from legislation_research import search_legislation
from statistics_research import search_statistics
from research_focus import research_guidance


BASE_DIR = Path(__file__).resolve().parent

server = Flask(__name__)
server.config["JSON_SORT_KEYS"] = False


@server.get("/")
def homepage():
    return send_file(BASE_DIR / "index.html")


@server.get("/johnsmythe-v1.js")
def website_javascript():
    return send_file(
        BASE_DIR / "johnsmythe-v1.js",
        mimetype="application/javascript",
    )


def normalize_record(record, default_source):
    """Convert different source records to a shared format."""

    source = record.get("source") or default_source

    return {
        "title": record.get("title") or "Untitled record",
        "date": record.get("date") or record.get("release_date"),
        "date_answered": record.get("date_answered"),
        "source": source,
        "reference": record.get("reference"),
        "record_id": record.get("record_id"),
        "department": record.get("department"),
        "question": record.get("question") or "",
        "answer": record.get("answer") or "",
        "description": record.get("description") or "",
        "document_type": record.get("document_type") or "",
        "url": record.get("url") or "",
        "verified": False,
        "relevance_analysis": record.get("relevance_analysis"),
        "search_relevance_score": record.get(
            "search_relevance_score"
        ),
    }


def filter_source_records(records, date_range):
    """
    Classify records by date without changing originals.
    """

    return classify_records_by_date(
        records,
        date_range,
    )


@server.post("/api/research")
def research():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid research request."
        }), 400

    question = str(data.get("question", "")).strip()

    if not question:
        return jsonify({
            "error": "Please enter a research question."
        }), 400

    if len(question) > 500:
        return jsonify({
            "error": "Question exceeds 500 characters."
        }), 400

    print("\n" + "=" * 55)
    print("JOHN SMYTHE - NEW RESEARCH REQUEST")
    print("Question:", question)
    print("=" * 55)

    investigation = ResearchAnalysis(question)
    checker = SourceCheck()
    source_plan = source_search_plan(question)

    date_range = extract_date_range(question)

    # ----------------------------------------------
    # RETRIEVE ALL FOUR OFFICIAL SOURCES CONCURRENTLY
    # ----------------------------------------------
    # Each source keeps its own search and error handling. The
    # results are processed below in the original report order.
    search_started = perf_counter()
    print("Starting four official-source searches together...", flush=True)

    with ThreadPoolExecutor(max_workers=4) as pool:
        parliament_future = pool.submit(search_parliament, question, limit=10)
        government_future = pool.submit(search_government, question, limit=10)
        legislation_future = pool.submit(search_legislation, question, limit=10)
        statistics_future = pool.submit(search_statistics, question, limit=10)

        parliamentary_records = parliament_future.result()
        parliamentary_records = rank_evidence(question, parliamentary_records)
        parliamentary_evidence = [
            normalize_record(record, "UK Parliament")
            for record in parliamentary_records
        ]
        parliamentary_dates = filter_source_records(parliamentary_evidence, date_range)
        parliamentary_evidence = parliamentary_dates["matching"]

        government_records = []
        government_error = None
        try:
            government_records = government_future.result()
        except RuntimeError as error:
            government_error = str(error)
            print("GOV.UK search error:", error)
        government_dates = filter_source_records(government_records, date_range)
        government_records = government_dates["matching"]
        government_records = rank_evidence(question, government_records)

        legislation_records = []
        legislation_error = None
        try:
            legislation_records = legislation_future.result()
        except RuntimeError as error:
            legislation_error = str(error)
            print("Legislation search error:", error)
        legislation_dates = filter_source_records(legislation_records, date_range)
        legislation_records = legislation_dates["matching"]
        legislation_records = rank_evidence(question, legislation_records)

        statistics_records = []
        statistics_error = None
        try:
            statistics_records = statistics_future.result()
        except RuntimeError as error:
            statistics_error = str(error)
            print("ONS statistics search error:", error)
        statistics_dates = filter_source_records(statistics_records, date_range)
        statistics_records = statistics_dates["matching"]
        statistics_records = rank_evidence(question, statistics_records)

    print(
        "Official-source retrieval took",
        round(perf_counter() - search_started, 1),
        "seconds",
        flush=True,
    )

    # ----------------------------------------------
    # COMBINE MATCHING RESEARCH RECORDS
    # ----------------------------------------------

    full_evidence = list(parliamentary_evidence)

    for record in government_records:
        full_evidence.append(
            normalize_record(record, "GOV.UK")
        )

    for record in legislation_records:
        full_evidence.append(
            normalize_record(record, "UK Legislation")
        )

    for record in statistics_records:
        full_evidence.append(
            normalize_record(
                record,
                "Office for National Statistics",
            )
        )

    # Rank combined evidence from all four sources
    full_evidence = rank_evidence(question, full_evidence)


    # ----------------------------------------------
    # PRESERVE EXCLUDED AND UNDATED RECORDS
    # ----------------------------------------------

    date_review = {
        "date_range": date_range,
        "excluded": [],
        "undated": [],
    }

    classifications = [
        parliamentary_dates,
        government_dates,
        legislation_dates,
        statistics_dates,
    ]

    for classification in classifications:
        date_review["excluded"].extend(
            classification["excluded"]
        )
        date_review["undated"].extend(
            classification["undated"]
        )

    date_review["excluded_count"] = len(
        date_review["excluded"]
    )
    date_review["undated_count"] = len(
        date_review["undated"]
    )

    # ----------------------------------------------
    # ANALYSIS AND SOURCECHECK
    # ----------------------------------------------

    for record in full_evidence:
        record["evidence_assessment"] = assess_record(
            question, record
        )
        investigation.add_evidence(
            title=record["title"],
            source=record["source"],
            date=record["date"],
            statement=(
                record["question"]
                or record["description"]
            ),
            url=record["url"],
            reference=record["reference"],
        )

        if record["url"]:
            checker.add_source(
                title=record["title"],
                url=record["url"],
                publisher=record["source"],
                publication_date=record["date"],
                reference=record["reference"],
            )

    # ----------------------------------------------
    # TIMELINE
    # ----------------------------------------------

    timeline_events = build_timeline(
        full_evidence,
        newest_first=False,
    )

    yearly_groups = group_by_year(timeline_events)

    timeline_summary = timeline_statistics(
        timeline_events
    )

    # ----------------------------------------------
    # LIMITATIONS
    # ----------------------------------------------

    investigation.add_limitation(
        "Search results are source discoveries, "
        "not independently verified findings."
    )

    investigation.add_limitation(
        "Relevance scores measure keyword overlap, "
        "not whether evidence proves a claim."
    )

    investigation.add_limitation(
        "Timeline dates represent source publication "
        "or parliamentary record dates, not necessarily "
        "dates when policies were implemented."
    )

    investigation.add_limitation(
        "Search coverage is limited and may omit "
        "important records or historical developments."
    )

    investigation.add_limitation(
        "Date filtering uses recorded dates and may "
        "exclude older publications relevant to later events."
    )

    investigation.add_limitation(
        "AI analysis and automatic verification "
        "are not yet enabled."
    )

    report = investigation.generate_report()

    report["evidence"] = full_evidence
    report["timeline"] = timeline_events
    report["timeline_by_year"] = yearly_groups
    report["timeline_statistics"] = timeline_summary
    report["retrieved_count"] = len(full_evidence)
    report["retrieved_at"] = datetime.now(
        timezone.utc
    ).isoformat()
    report["status"] = "Unverified source discovery"
    report["date_review"] = date_review

    print("\nResearch completed.")
    print("Total records:", len(full_evidence))
    print("Timeline events:", len(timeline_events))
    print("Date-excluded records:", date_review["excluded_count"])
    print("Undated records:", date_review["undated_count"])

    return jsonify({
        "question": question,
        "report": report,
        "source_plan": source_plan,
        "research_guidance": research_guidance(question),
        "government_research": {
            "records": government_records,
            "retrieved_count": len(government_records),
            "error": government_error,
            "status": "Unverified government search results",
        },
        "legislation_research": {
            "records": legislation_records,
            "retrieved_count": len(legislation_records),
            "error": legislation_error,
            "status": "Unverified legislation search results",
        },
        "statistics_research": {
            "records": statistics_records,
            "retrieved_count": len(statistics_records),
            "error": statistics_error,
            "status": "Unverified statistical search results",
        },
        "sourcecheck": {
            "summary": checker.summary(),
            "sources": checker.list_sources(),
        },
    })


if __name__ == "__main__":

    print("=" * 55)
    print("JOHN SMYTHE RESEARCH ENGINE")
    print("You ask. We investigate. You decide.")
    print("=" * 55)

    print("\nStarting local research server...")
    print("Website: http://127.0.0.1:5000")
    print("Development mode - not publicly accessible\n")

    server.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )
