"""
JOHN SMYTHE RESEARCH ENGINE
Evidence Relevance - Version 0.3

Transparent topical relevance scoring.

Features:
- Exact keyword matching
- Related topic matching
- Title and question weighting
- Parliamentary answer and description matching
- Separate treatment of exact and related matches

Relevance is not evidence verification.
"""

import re


STOP_WORDS = {
    "what", "when", "where", "which", "who", "why",
    "how", "has", "have", "had", "was", "were",
    "the", "and", "for", "from", "with", "about",
    "into", "that", "this", "between", "since",
    "before", "after", "during", "does", "did",
    "government", "uk", "united", "kingdom",
    "parliament", "taken", "take", "taking",
    "action", "address", "steps", "recent",
    "year", "years", "policy", "policies",
}


NORMAL_FORMS = {
    "homeless": "homelessness",
    "houses": "housing",
    "house": "housing",
    "homes": "housing",
    "policies": "policy",
    "children": "child",
    "families": "family",
    "statistics": "statistic",
    "statistical": "statistic",
    "laws": "law",
    "jobs": "employment",
    "unemployed": "unemployment",
    "immigrants": "immigration",
    "immigrant": "immigration",
    "migrants": "migration",
    "migrant": "migration",
    "refugees": "refugee",
}


RELATED_TOPICS = {
    "homelessness": {
        "housing", "accommodation",
        "rough", "sleeping",
    },
    "housing": {
        "homelessness", "accommodation",
    },
    "accommodation": {
        "housing", "homelessness",
    },
    "employment": {
        "unemployment", "workforce",
    },
    "unemployment": {
        "employment", "workforce",
    },
    "immigration": {
        "migration", "migrant", "asylum",
    },
    "asylum": {
        "refugee", "immigration",
    },
}


def normalize_word(word):
    return NORMAL_FORMS.get(word, word)


def keywords(text):
    words = re.findall(
        r"[a-z0-9]+",
        str(text).lower(),
    )

    return {
        normalize_word(word)
        for word in words
        if len(word) > 2
        and word not in STOP_WORDS
        and not (
            len(word) == 4 and word.isdigit()
        )
    }


def calculate_relevance(question, record):
    """
    Estimate topical relevance.

    Exact matches score more highly than
    related topic matches.
    """

    question_words = keywords(question)

    if not question_words:
        return {
            "score": 0,
            "matched_keywords": [],
            "relevance": "Unknown",
        }

    title_words = keywords(
        record.get("title") or ""
    )

    question_text_words = keywords(
        record.get("question") or ""
    )

    other_words = keywords(
        " ".join([
            str(record.get("answer") or ""),
            str(record.get("description") or ""),
        ])
    )

    matched_keywords = set()
    total_points = 0

    for word in question_words:

        related = RELATED_TOPICS.get(word, set())

        if word in title_words:
            points = 6
            matched_keywords.add(word)

        elif word in question_text_words:
            points = 5
            matched_keywords.add(word)

        elif word in other_words:
            points = 3
            matched_keywords.add(word)

        elif related.intersection(title_words):
            points = 3
            matched_keywords.update(
                related.intersection(title_words)
            )

        elif related.intersection(question_text_words):
            points = 2
            matched_keywords.update(
                related.intersection(question_text_words)
            )

        elif related.intersection(other_words):
            points = 1
            matched_keywords.update(
                related.intersection(other_words)
            )

        else:
            points = 0

        total_points += points

    maximum_points = len(question_words) * 6

    score = min(
        100,
        round(total_points / maximum_points * 100)
    )

    if score >= 70:
        relevance = "High"
    elif score >= 35:
        relevance = "Moderate"
    elif score > 0:
        relevance = "Low"
    else:
        relevance = "No keyword match"

    return {
        "score": score,
        "matched_keywords": sorted(matched_keywords),
        "relevance": relevance,
    }


def rank_evidence(question, records):
    """Rank source records by topical relevance."""

    ranked = []

    for record in records:
        item = dict(record)

        item["relevance_analysis"] = (
            calculate_relevance(question, item)
        )

        ranked.append(item)

    return sorted(
        ranked,
        key=lambda item: item[
            "relevance_analysis"
        ]["score"],
        reverse=True,
    )


if __name__ == "__main__":

    question = "UK homelessness policy"

    sample_records = [
        {
            "title": "Homelessness Reduction Act",
            "question": "How will homelessness be reduced?",
            "answer": "Local authorities have duties.",
        },
        {
            "title": "Temporary Accommodation",
            "question": "What housing support is available?",
            "answer": "Councils provide assistance.",
        },
        {
            "title": "Unrelated subject",
            "question": "What are the arrangements?",
            "answer": "No relevant information.",
        },
    ]

    for record in rank_evidence(question, sample_records):
        result = record["relevance_analysis"]

        print(
            result["score"],
            result["relevance"],
            "-",
            record["title"],
        )