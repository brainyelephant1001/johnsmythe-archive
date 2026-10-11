
"""
JOHN SMYTHE RESEARCH ENGINE
GOV.UK Research Module — Version 0.2

You ask. We investigate. You decide.

Focused GOV.UK searches with keyword-based
relevance filtering.

Results remain unverified evidence leads.
"""

import json
import re
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


SEARCH_URL = "https://www.gov.uk/api/search.json"
BASE_URL = "https://www.gov.uk"

STOP_WORDS = {
    "what", "which", "when", "where", "why", "how",
    "has", "have", "had", "the", "and", "for",
    "from", "with", "into", "about", "since",
    "taken", "take", "action", "address",
    "government", "parliament", "uk", "british",
    "been", "were", "was", "are", "does",
    "did", "its", "their", "this", "that",
    "policy", "policies", "steps", "recent",
    "year", "years",
}


def research_terms(question):
    """Extract meaningful words from a question."""

    words = re.findall(r"[a-zA-Z]{3,}", question.lower())

    return list(dict.fromkeys(
        word for word in words
        if word not in STOP_WORDS
    ))


def search_government(question, limit=10):
    """Retrieve and strictly rank official government publication leads."""
    from concurrent.futures import ThreadPoolExecutor
    from research_focus import government_queries, government_score
    question = str(question).strip()
    if not question:
        return []
    limit = max(1, min(int(limit), 50))
    queries = government_queries(question)
    if not queries:
        return []

    def retrieve(query):
        url = SEARCH_URL + "?" + urlencode({"q": query, "count": 50})
        req = Request(url, headers={"User-Agent": "JohnSmytheResearch/0.7", "Accept": "application/json"})
        with urlopen(req, timeout=8) as response:
            data = json.load(response)
        if not isinstance(data, dict) or not isinstance(data.get("results"), list):
            raise RuntimeError("Unexpected GOV.UK search response")
        return data["results"]

    candidates = []
    failures = []
    with ThreadPoolExecutor(max_workers=min(2, len(queries))) as pool:
        futures = [pool.submit(retrieve, q) for q in queries]
        for future in futures:
            try:
                candidates.extend(future.result())
            except Exception as error:
                failures.append(str(error))
    if not candidates and failures:
        raise RuntimeError("GOV.UK unavailable: " + failures[0])
    ranked = []
    seen = set()
    for item in candidates:
        if not isinstance(item, dict):
            continue
        path = item.get("link", "")
        if not isinstance(path, str) or not path.startswith("/") or path.startswith("//"):
            continue
        title = str(item.get("title") or "")
        description = str(item.get("description") or "")
        score = government_score(question, title, description)
        if score <= 0 or path in seen:
            continue
        seen.add(path)
        ranked.append({
            "source": "GOV.UK", "source_type": "Government publication",
            "title": title or "Untitled publication", "description": description,
            "date": item.get("public_timestamp") or item.get("first_published_at") or "",
            "url": urljoin(BASE_URL, path), "document_type": item.get("format") or "",
            "verified": False, "verification_status": "Official source lead; contents not independently checked",
            "search_relevance_score": score,
        })
    ranked.sort(key=lambda r: (-r["search_relevance_score"], r["title"]))
    return ranked[:limit]


if __name__ == "__main__":
    question = input(
        "Enter a government research question: "
    )

    try:
        results = search_government(question)

        print("\nGOV.UK search results:", len(results))

        for record in results:
            print("\nTitle:", record["title"])
            print("Date:", record["date"])
            print("Type:", record["document_type"])
            print("URL:", record["url"])

    except RuntimeError as error:
        print("\nError:", error)
