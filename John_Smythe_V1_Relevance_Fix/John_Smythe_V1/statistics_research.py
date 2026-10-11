
"""
JOHN SMYTHE RESEARCH ENGINE
ONS Statistics Research — Version 0.2

You ask. We investigate. You decide.

Discovers relevant Office for National Statistics
datasets and statistical time series.

Search results are source discoveries, not verified
statistical findings or evidence of causation.
"""

import json
import re
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


SEARCH_URL = "https://api.beta.ons.gov.uk/v1/search"
ONS_WEBSITE = "https://www.ons.gov.uk"

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be",
    "by", "can", "did", "do", "does", "for",
    "from", "government", "has", "have", "how",
    "in", "is", "it", "of", "on", "or",
    "our", "policy", "policies", "research",
    "show", "statistics", "statistical", "the",
    "their", "there", "to", "uk", "united",
    "kingdom", "was", "were", "what", "when",
    "where", "which", "who", "why", "with",
}


def official_ons_url(uri):
    """Convert an ONS page path into a safe website URL."""

    if not isinstance(uri, str) or not uri:
        return ""

    if uri.startswith("/") and not uri.startswith("//"):
        return ONS_WEBSITE + uri

    parsed = urlparse(uri)

    if (
        parsed.scheme == "https"
        and parsed.hostname in (
            "www.ons.gov.uk",
            "ons.gov.uk",
        )
    ):
        return uri

    return ""


def important_words(text):
    """Extract meaningful search words."""

    words = re.findall(
        r"[a-z0-9]+",
        str(text).lower()
    )

    return {
        word
        for word in words
        if len(word) >= 3 and word not in STOP_WORDS
    }


def relevance_score(question_words, title, description):
    """
    Measure keyword overlap.

    Title matches receive more weight than
    description matches.

    This is not a measure of factual accuracy.
    """

    title_words = important_words(title)
    description_words = important_words(description)

    title_matches = question_words & title_words
    description_matches = question_words & description_words

    score = (
        len(title_matches) * 3
        + len(description_matches)
    )

    return score



def search_statistics(question, limit=10):
    """
    Discover relevant ONS datasets and time series.

    Returns search-result metadata, not data values.
    """

    question = str(question).strip()

    if not question:
        return []

    limit = max(1, min(int(limit), 50))

    # Distinguish a named Act from a statistical question.
    named_act = re.search(
        r"\b[A-Za-z][A-Za-z,\s-]*?\s+Act\s+\d{4}\b",
        question,
        flags=re.IGNORECASE
    )

    statistical_intent = bool(
        re.search(
            r"\b(statistics|statistical|data|figures|"
            r"rates|trends|numbers|percentage|"
            r"population|how many)\b",
            question,
            flags=re.IGNORECASE
        )
    )

    if named_act and not statistical_intent:
        return []

    keywords = important_words(question)

    if not keywords:
        return []

    search_query = " ".join(sorted(keywords))
    candidate_limit = min(max(limit * 5, 30), 100)

    parameters = urlencode({
        "q": search_query,
        "limit": candidate_limit,
        "offset": 0,
    })

    url = SEARCH_URL + "?" + parameters

    request = Request(
        url,
        headers={
            "User-Agent": "JohnSmytheResearch/0.2",
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=8) as response:
            data = json.load(response)

    except (
        HTTPError,
        URLError,
        TimeoutError,
        ValueError,
    ) as error:
        raise RuntimeError(
            "ONS statistics search request failed"
        ) from error

    if not isinstance(data, dict):
        raise RuntimeError(
            "Unexpected ONS search response"
        )

    items = data.get("items")

    if not isinstance(items, list):
        raise RuntimeError(
            "ONS search response has no valid items list"
        )

    records = []

    for item in items:
        if not isinstance(item, dict):
            continue

        title = item.get("title") or "Untitled statistic"

        summary = (
            item.get("summary")
            or item.get("meta_description")
            or ""
        )

        score = relevance_score(
            keywords,
            title,
            summary
        )

        if score == 0:
            continue

        records.append({
            "source": "Office for National Statistics",
            "source_type": "Official statistics",
            "title": title,
            "description": summary,
            "document_type": item.get("type") or "",
            "dataset_id": item.get("dataset_id") or "",
            "series_id": item.get("cdid") or "",
            "release_date": item.get("release_date") or "",
            "url": official_ons_url(item.get("uri")),
            "relevance_score": score,
            "verified": False,
            "verification_status": (
                "ONS search result; statistical data "
                "and methodology not yet assessed"
            ),
        })


    # Remove duplicate ONS release announcements.
    published_titles = {
        record["title"].lower().replace('"', "").strip()
        for record in records
        if "/releases/" not in record["url"]
    }

    seen_urls = set()
    filtered_records = []

    for record in records:
        url = record["url"].rstrip("/").lower()
        title = record["title"].lower().replace('"', "").strip()

        if url in seen_urls:
            continue

        if "/releases/" in url and title in published_titles:
            continue

        seen_urls.add(url)
        filtered_records.append(record)

    records = filtered_records


    records.sort(
        key=lambda record: record["relevance_score"],
        reverse=True
    )

    return records[:limit]


if __name__ == "__main__":

    question = input(
        "Enter a statistical research question: "
    )

    try:
        results = search_statistics(question)

        print("\nRelevant ONS results:", len(results))

        for record in results:
            print("\nTitle:", record["title"])
            print("Relevance score:", record["relevance_score"])
            print("Type:", record["document_type"])
            print("Released:", record["release_date"])
            print("URL:", record["url"])

    except RuntimeError as error:
        print("\nError:", error)
