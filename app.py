
"""
JOHN SMYTHE RESEARCH ENGINE
Parliamentary Search Backend — Version 0.5

You ask. We investigate. You decide.

Improved relevance filtering and historical coverage.

Records are official source discoveries, not verified findings.
"""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import socket
import urllib.error
import urllib.parse
import urllib.request

from datetime import datetime, timezone

from search_engine import generate_search_terms
from historical_search import extract_date_range


PARLIAMENT_API = (
    "https://questions-statements-api.parliament.uk"
    "/api/writtenquestions/questions"
)

HANSARD_API = (
    "https://hansard-api.parliament.uk/search.json"
)
REQUEST_TIMEOUT = 6
DEFAULT_RESULTS = 10

STOP_WORDS = {
    "what", "when", "where", "which", "who", "why", "how",
    "has", "have", "had", "the", "and", "for", "from",
    "with", "about", "since", "between", "during", "into",
    "said", "say", "does", "did", "was", "were", "are",
    "been", "that", "this", "their", "there", "its",
    "government", "united", "kingdom", "british",
    "policy", "policies", "year", "years", "uk",
}

TOPIC_ALIASES = {
    "immigration": {
        "immigration", "immigrant", "immigrants",
        "migrant", "migrants", "migration",
    },
    "asylum": {
        "asylum", "refugee", "refugees",
    },
    "housing": {
        "housing", "homes", "homelessness",
        "accommodation",
    },
    "employment": {
        "employment", "unemployment", "jobs",
        "workforce",
    },
}


def keywords(text):
    """Extract meaningful topic words."""

    words = re.findall(
        r"[a-z]+",
        str(text).lower()
    )

    return {
        word for word in words
        if len(word) >= 3
        and word not in STOP_WORDS
    }


def expanded_keywords(question):
    """Include a small set of related topic expressions."""

    original = keywords(question)
    expanded = set(original)

    for topic, aliases in TOPIC_ALIASES.items():
        if topic in original or original.intersection(aliases):
            expanded.update(aliases)

    return original, expanded


def relevance_score(question, record):
    """
    Calculate a basic topic-match score.

    This is keyword matching, not AI verification.
    """

    original, expanded = expanded_keywords(question)

    if not original:
        return 0

    title = keywords(record.get("title", ""))
    question_text = keywords(record.get("question", ""))
    answer_text = keywords(record.get("answer", ""))

    title_matches = title.intersection(expanded)
    question_matches = question_text.intersection(expanded)
    answer_matches = answer_text.intersection(expanded)

    score = (
        len(title_matches) * 5
        + len(question_matches) * 3
        + len(answer_matches)
    )
    # Give an exact multiword phrase in the title substantially more weight
    # than an incidental mention inside a lengthy parliamentary contribution.
    phrase = re.sub(r"\s+", " ", str(question).strip()).lower()
    title_plain = re.sub(r"\s+", " ", str(record.get("title") or "")).lower()
    if len(phrase.split()) >= 2 and phrase in title_plain:
        score += 30

    # Require at least one topic match in the
    # title or parliamentary question itself.
    if not title_matches and not question_matches:
        return 0

    return score


def date_windows(start_year, end_year):
    """
    Split historical searches into up to three periods.

    This helps avoid retrieving only recent records.
    """

    if start_year is None and end_year is None:
        return [(None, None)]

    if start_year is None:
        return [(None, end_year)]

    if end_year is None:
        end_year = datetime.now(timezone.utc).year

    start_year = int(start_year)
    end_year = int(end_year)

    if start_year > end_year:
        start_year, end_year = end_year, start_year

    number_of_years = end_year - start_year + 1

    if number_of_years <= 3:
        return [(start_year, end_year)]

    window_size = (number_of_years + 2) // 3
    windows = []

    year = start_year

    while year <= end_year:
        window_end = min(
            year + window_size - 1,
            end_year
        )

        windows.append((year, window_end))
        year = window_end + 1

    return windows


def retrieve_parliament_records(
    search_term,
    limit,
    start_year=None,
    end_year=None,
    skip=0,
):
    """Retrieve parliamentary search results."""

    parameters = {
        "searchTerm": search_term,
        "take": limit,
        "skip": skip,
    }

    if start_year is not None:
        parameters["tabledWhenFrom"] = (
            f"{start_year}-01-01"
        )

    if end_year is not None:
        parameters["tabledWhenTo"] = (
            f"{end_year}-12-31"
        )

    url = PARLIAMENT_API + "?" + urllib.parse.urlencode(
        parameters
    )

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "JohnSmytheResearch/0.5",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT
        ) as response:
            data = json.load(response)

    except (
        urllib.error.URLError,
        TimeoutError,
        socket.timeout,
        OSError,
        ValueError,
    ) as error:
        print("Parliament search failed:", error)
        # Do not launch a second slow network request on a failed API call.
        return []

    if not isinstance(data, dict):
        return []

    results = []

    for item in data.get("results", []):

        if not isinstance(item, dict):
            continue

        record = item.get("value", item)

        if not isinstance(record, dict):
            continue

        record_id = record.get("id")

        source_url = ""

        if record_id is not None:
            source_url = (
                PARLIAMENT_API + "/" + str(record_id)
            )

        results.append({
            "title": (
                record.get("heading")
                or record.get("questionText")
                or "Parliamentary question"
            ),
            "date": record.get("dateTabled"),
            "date_answered": record.get("dateAnswered"),
            "source": "UK Parliament",
            "reference": record.get("uin"),
            "record_id": record_id,
            "department": record.get("answeringBodyName"),
            "question": record.get("questionText") or "",
            # The list API may already include an answer excerpt.
            # Never fetch every individual answer during discovery.
            "answer": clean_parliament_answer(record.get("answerText") or ""),
            "url": source_url,
            "verified": False,
        })

    return results


def clean_parliament_answer(answer):
    """Convert parliamentary HTML answers into readable plain text."""
    import html
    import re

    if not answer:
        return ""

    answer = re.sub(
        r"<\s*br\s*/?\s*>",
        "\n",
        answer,
        flags=re.IGNORECASE,
    )

    answer = re.sub(
        r"</\s*p\s*>",
        "\n\n",
        answer,
        flags=re.IGNORECASE,
    )

    answer = re.sub(r"<[^>]+>", "", answer)
    answer = html.unescape(answer)

    return answer.strip()


def retrieve_full_parliament_answer(record_id, fallback_answer=""):
    """Retrieve the complete answer from an individual Parliament record."""

    if record_id is None:
        return fallback_answer

    url = PARLIAMENT_API + "/" + str(record_id)

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "JohnSmytheResearch/0.5",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            data = json.load(response)

        record = data.get("value", data)
        answer = record.get("answerText") or fallback_answer
        return clean_parliament_answer(answer)

    except (
        urllib.error.URLError,
        TimeoutError,
        socket.timeout,
        OSError,
        ValueError,
        AttributeError,
    ) as error:
        print("Full Parliament answer unavailable:", error)
        return fallback_answer


def retrieve_hansard_records(search_term, limit=10, start_year=None, end_year=None):
    """Retrieve parliamentary records from the official Hansard API."""

    # Preserve the API request already tested successfully on the Dell.
    parameters = {"searchTerm": search_term}
    url = HANSARD_API + "?" + urllib.parse.urlencode(parameters)

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "JohnSmytheResearch/0.5",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            data = json.load(response)
    except (
        urllib.error.URLError,
        TimeoutError,
        socket.timeout,
        OSError,
        ValueError,
    ) as error:
        print("Hansard search failed:", error)
        return []

    if not isinstance(data, dict):
        print("Hansard returned unexpected response format", flush=True)
        return []

    results = []
    seen_ids = set()

    categories = [
        ("Contributions", "Parliamentary contribution"),
        ("WrittenStatements", "Written statement"),
        ("WrittenAnswers", "Written answer"),
        ("Debates", "Parliamentary debate"),
    ]

    for category, label in categories:
        items = data.get(category, [])
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue

            date = item.get("SittingDate", "")
            year = int(date[:4]) if date[:4].isdigit() else None

            if start_year is not None and (year is None or year < start_year):
                continue
            if end_year is not None and (year is None or year > end_year):
                continue

            record_id = item.get("ContributionExtId") or item.get(
                "DebateSectionExtId"
            ) or item.get("ItemId")

            if record_id in seen_ids:
                continue
            seen_ids.add(record_id)

            title = (
                item.get("Title")
                or item.get("DebateSection")
                or label
            )

            # Link to the particular debate, not the Hansard homepage.
            # The debate GUID, sitting date and title are supplied by Hansard.
            sitting_day = str(date)[:10]
            house = str(item.get("House", "")).strip().lower()
            house_segment = "Lords" if house == "lords" else (
                "Commons" if house == "commons" else ""
            )
            debate_id = item.get("DebateSectionExtId")
            debate_title = str(item.get("DebateSection") or title or "")
            title_slug = "".join(re.findall(r"[A-Za-z0-9]+", debate_title))
            if debate_id and house_segment and re.fullmatch(r"\d{4}-\d{2}-\d{2}", sitting_day):
                source_url = (
                    f"https://hansard.parliament.uk/{house_segment}/"
                    f"{sitting_day}/debates/{debate_id}"
                    + (f"/{title_slug}" if title_slug else "")
                )
            elif house_segment and re.fullmatch(r"\d{4}-\d{2}-\d{2}", sitting_day):
                source_url = f"https://hansard.parliament.uk/{house_segment}/{sitting_day}"
            else:
                source_url = "https://hansard.parliament.uk/"

            contribution_text = clean_parliament_answer(item.get("ContributionText") or "")
            full_text = clean_parliament_answer(item.get("ContributionTextFull") or "")
            # Debate-heading hits with no substantive text cannot be assessed.
            # The contributions that follow provide the actual evidence text.
            if not contribution_text and not full_text:
                continue

            results.append({
                "title": title,
                "date": date,
                "source": "UK Parliament Hansard",
                "reference": str(record_id or ""),
                "record_id": str(record_id or ""),
                "department": item.get("House", ""),
                "question": contribution_text,
                "answer": full_text,
                "url": source_url,
                "verified": False,
            })

            if len(results) >= limit:
                return results

    return results


def search_parliament(question, limit=DEFAULT_RESULTS):
    """Bounded, parallel discovery of official Parliamentary records.

    This is source discovery, not an exhaustive search or legal analysis.
    Failed searches return partial results rather than blocking the website.
    """
    question = str(question).strip()
    if not question:
        return []

    try:
        limit = max(1, min(int(limit), 50))
    except (TypeError, ValueError):
        limit = DEFAULT_RESULTS

    plan = generate_search_terms(question)
    terms = plan.get("search_terms", []) if isinstance(plan, dict) else (
        plan if isinstance(plan, (list, tuple)) else []
    )

    # Multiword legal phrases carry more meaning than isolated generic words.
    phrase_candidates = []
    lowered = question.lower()
    if "telecommunication" in lowered or "mobile" in lowered or "phone" in lowered:
        phrase_candidates.extend(["telecommunications contracts", "mobile phone contracts"])
    if "mis-selling" in lowered or "misselling" in lowered or "misrepresentation" in lowered:
        phrase_candidates.extend(["mis-selling", "misrepresentation"])
    if "consumer" in lowered:
        phrase_candidates.append("consumer protection")

    generic = {"against", "available", "legislation", "protect", "protects", "laws",
               "law", "contract", "contracts", "consumer", "consumers", "legal",
               "remedies", "rights", "unfair", "terms", "breaches"}
    topic_words = sorted((keywords(question) - generic), key=lambda x: (-len(x), x))
    candidates = phrase_candidates + list(terms) + topic_words
    unique_terms = []
    seen = set()
    for term in candidates:
        term = str(term).strip()
        if not term or term.lower() in seen or term.lower() in generic:
            continue
        seen.add(term.lower())
        unique_terms.append(term)
        if len(unique_terms) == 3:
            break
    if not unique_terms:
        unique_terms = topic_words[:2] or [question[:80]]

    # A year in legislation's title is not a requested date filter.
    # Preserve separately requested years, e.g. "Consumer Rights Act 2015 in 2023".
    date_query = re.sub(
        r"\b(?:Act|Regulations|Order)\s+(?:19|20)\d{2}\b",
        "", question, flags=re.IGNORECASE,
    )
    dates = extract_date_range(date_query)
    windows = date_windows(dates.get("start_year"), dates.get("end_year"))
    # Cap broad historical searches to avoid a combinatorial number of calls.
    jobs = [(term, start, end) for term in unique_terms for start, end in windows][:6]
    print("Parliament search terms:", unique_terms, flush=True)
    print("Parliament API searches:", len(jobs), flush=True)

    records = []
    with ThreadPoolExecutor(max_workers=min(6, len(jobs))) as pool:
        futures = [pool.submit(retrieve_parliament_records, term, 15, start, end)
                   for term, start, end in jobs]
        for future in as_completed(futures):
            try:
                records.extend(future.result())
            except Exception as error:
                print("Parliament search error:", error, flush=True)

    findings = []
    seen_ids = set()
    for record in records:
        identifier = record.get("record_id") or (
            record.get("reference"), record.get("date"), record.get("title")
        )
        if identifier in seen_ids:
            continue
        seen_ids.add(identifier)
        score = relevance_score(question, record)
        if score > 0:
            record["search_relevance_score"] = score
            findings.append(record)

    # When Written Questions produces no relevant records (including on API
    # failure), attempt one bounded Hansard query rather than returning zero.
    if not findings:
        fallback_term = question.strip()
        print("Trying Hansard fallback:", fallback_term, flush=True)
        for record in retrieve_hansard_records(
            fallback_term, limit=limit,
            start_year=dates.get("start_year"),
            end_year=dates.get("end_year"),
        ):
            score = relevance_score(question, record)
            if score > 0:
                record["search_relevance_score"] = score
                findings.append(record)

    findings.sort(key=lambda r: (-r["search_relevance_score"], str(r.get("date") or "")))
    selected = findings[:limit]

    # Fetch complete answers only for the final selected written questions.
    # Fetching every search candidate would be unnecessarily slow.
    questions = [r for r in selected if r.get("source") == "UK Parliament"
                 and r.get("record_id") is not None]
    if questions:
        with ThreadPoolExecutor(max_workers=min(4, len(questions))) as pool:
            futures = {
                pool.submit(retrieve_full_parliament_answer,
                            r["record_id"], r.get("answer", "")): r
                for r in questions
            }
            for future in as_completed(futures):
                record = futures[future]
                try:
                    complete = future.result()
                    if complete:
                        record["answer"] = complete
                except Exception as error:
                    print("Parliament answer lookup failed:", error, flush=True)

    print("Parliament candidates:", len(findings), "selected:", len(selected), flush=True)
    return selected


def main():

    print("=" * 55)
    print("JOHN SMYTHE RESEARCH ENGINE")
    print("You ask. We investigate. You decide.")
    print("=" * 55)

    question = input(
        "\nWhat would you like to investigate?\n> "
    ).strip()

    if not question:
        print("Please enter a research question.")
        return

    findings = search_parliament(question)

    report = {
        "question": question,
        "created": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": "Unverified source discovery",
        "results": findings,
    }

    with open(
        "research-results.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("\nRecords found:", len(findings))
    print("Results saved to research-results.json")


if __name__ == "__main__":
    main()
