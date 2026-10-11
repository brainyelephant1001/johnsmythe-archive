
"""
JOHN SMYTHE RESEARCH ENGINE
UK Legislation Research — Version 0.2

You ask. We investigate. You decide.

Searches official legislation.gov.uk Atom feeds.
Search results are not legal interpretations.
"""

import re
import ssl
import certifi
import xml.etree.ElementTree as ET
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


SEARCH_URL = "https://www.legislation.gov.uk/all/data.feed"
ATOM = "{http://www.w3.org/2005/Atom}"

STOP_WORDS = {
    "a", "an", "and", "are", "about", "by", "can",
    "does", "do", "for", "from", "government",
    "how", "in", "is", "law", "laws", "legislation",
    "of", "on", "policy", "policies", "regarding",
    "related", "research", "the", "to", "uk",
    "united", "kingdom", "what", "when", "which",
    "who", "why", "with",
}

# Only use a synonym when the meaning is sufficiently clear.
SEARCH_ALIASES = {
    "homeless": "homelessness",
    "unemployed": "unemployment",
    "evictions": "eviction",
    "tenants": "tenant",
}


def get_text(entry, name):
    """Read text from an Atom XML element."""
    value = entry.findtext(ATOM + name)
    return (value or "").strip()


def get_title(entry):
    """
    Read an English title where available.

    Some bilingual legislation entries contain title text
    inside language-labelled child elements.
    """
    title_element = entry.find(ATOM + "title")

    if title_element is None:
        return "Untitled legislation"

    direct_text = (title_element.text or "").strip()

    if direct_text:
        return direct_text

    for child in title_element.iter():
        if child is title_element:
            continue

        language = child.get(
            "{http://www.w3.org/XML/1998/namespace}lang",
            "",
        )

        if language == "en":
            title = "".join(child.itertext()).strip()
            if title:
                return title

    title = " ".join(
        text.strip()
        for text in title_element.itertext()
        if text.strip()
    )

    return title or "Untitled legislation"


def get_legislation_link(entry):
    """Find an official legislation webpage."""

    for link in entry.findall(ATOM + "link"):
        href = link.get("href", "")
        relation = link.get("rel", "")

        if relation not in ("alternate", ""):
            continue

        if href.startswith("/") and not href.startswith("//"):
            href = "https://www.legislation.gov.uk" + href

        parsed = urlparse(href)

        if parsed.hostname not in (
            "www.legislation.gov.uk",
            "legislation.gov.uk",
        ):
            continue

        if parsed.scheme not in ("http", "https"):
            continue

        # Prefer the main legislation page, not an XML/PDF file.
        if parsed.path.endswith((
            ".xml", ".rdf", ".akn", ".xht",
            ".html", ".htm", ".csv", ".pdf",
        )):
            continue

        if parsed.scheme == "http":
            href = parsed._replace(scheme="https").geturl()

        return href

    return ""


def get_search_terms(question):
    """
    Extract meaningful terms from a research question.

    Example:
        UK homelessness policy -> homelessness
    """
    words = re.findall(
        r"[a-zA-Z]+",
        str(question).lower(),
    )

    terms = []

    for word in words:
        if word in STOP_WORDS or len(word) < 3:
            continue

        word = SEARCH_ALIASES.get(word, word)

        if word not in terms:
            terms.append(word)

    return terms


def fetch_legislation(term, limit):
    """Retrieve legislation metadata for one search term."""

    parameters = urlencode({
        "title": term,
        "results-count": limit,
        "sort": "basic",
    })

    url = SEARCH_URL + "?" + parameters

    request = Request(
        url,
        headers={
            "User-Agent": "JohnSmytheResearch/0.2",
            "Accept": "application/atom+xml",
        },
    )

    try:
        with urlopen(request, timeout=8, context=ssl.create_default_context(cafile=certifi.where())) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)

    except (
        HTTPError,
        URLError,
        TimeoutError,
        ET.ParseError,
    ) as error:
        raise RuntimeError(
            f"Legislation search request failed: {error}"
        ) from error

    if root.tag != ATOM + "feed":
        raise RuntimeError(
            "Unexpected legislation API response"
        )

    records = []
    for entry in root.findall(ATOM + "entry"):
        title = get_title(entry)
        updated = get_text(entry, "updated")
        published = get_text(entry, "published")
        identifier = get_text(entry, "id")
        records.append({
            "source": "legislation.gov.uk",
            "source_type": "Legislation",
            "title": title,
            "date": published,
            "last_updated": updated,
            "identifier": identifier,
            "url": get_legislation_link(entry),
            "verified": False,
            "verification_status": (
                "Official legislation search result; "
                "legal status not independently assessed"
            ),
        })

    return records


def search_legislation(question, limit=10):
    """Search official legislation; exclude unrelated titles rather than fill slots."""
    from concurrent.futures import ThreadPoolExecutor
    from research_focus import legislation_queries, legislation_score
    question = str(question).strip()
    if not question:
        return []
    limit = max(1, min(int(limit), 50))
    terms = legislation_queries(question)
    if not terms:
        return []
    results = []
    failures = []
    with ThreadPoolExecutor(max_workers=min(4, len(terms))) as pool:
        futures = [(term, pool.submit(fetch_legislation, term, 30)) for term in terms]
        for term, future in futures:
            try:
                for record in future.result():
                    score = legislation_score(question, record.get("title", ""), term)
                    if score > 0:
                        record["search_relevance_score"] = score
                        results.append(record)
            except Exception as error:
                failures.append(str(error))
    if not results and failures and len(failures) == len(terms):
        raise RuntimeError("Legislation source unavailable: " + failures[0])
    seen = set()
    filtered = []
    for record in sorted(results, key=lambda r: -r["search_relevance_score"]):
        key = record.get("identifier") or record.get("url") or record.get("title")
        if key in seen:
            continue
        seen.add(key)
        filtered.append(record)
        if len(filtered) >= limit:
            break
    return filtered


if __name__ == "__main__":
    question = input(
        "Enter legislation search terms: "
    )

    try:
        results = search_legislation(question)

        print("\nLegislation results:", len(results))

        for record in results:
            print("\nTitle:", record["title"])
            print("Published:", record["date"])
            print("Updated:", record["last_updated"])
            print("URL:", record["url"])

    except RuntimeError as error:
        print("\nError:", error)
