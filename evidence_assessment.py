
"""
John Smythe Research Engine
Evidence Assessment - Experimental Version 0.1

Classifies how closely a record relates to a research question.
This is a rule-based assessment, not independent fact-checking.
"""

import re


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "by",
    "do", "does", "for", "from", "has", "have", "how", "in",
    "is", "it", "of", "on", "or", "since", "that", "the",
    "their", "there", "these", "this", "to", "was", "were",
    "what", "when", "where", "which", "who", "will", "with",
    "uk", "parliament", "government", "taken", "taking",
    "take", "action", "address", "steps", "year", "years"
}

RELATED_TERMS = {
    "homeless": "homelessness",
    "homelessness": "homelessness",
    "families": "family",
    "family": "family",
    "children": "child",
    "child": "child",
    "houses": "housing",
    "homes": "housing",
}


def normalise_word(word):
    word = word.lower()
    return RELATED_TERMS.get(word, word)


def extract_keywords(text):
    words = re.findall(r"[a-zA-Z]+", str(text).lower())
    return {
        normalise_word(word)
        for word in words
        if len(word) > 2 and word not in STOPWORDS
    }


def assess_evidence(question, record):
    """
    Return a preliminary relevance category for a record.

    This does not verify the record's accuracy or determine
    whether the record proves any particular claim.
    """
    title = str(record.get("title") or "")
    description = str(record.get("description") or "")
    question_text = str(record.get("question") or "")
    answer = str(record.get("answer") or "")
    content = str(record.get("content") or "")

    keywords = extract_keywords(question)

    title_words = extract_keywords(title)
    body_words = extract_keywords(
        " ".join([description, question_text, answer, content])
    )

    title_matches = sorted(keywords & title_words)
    body_matches = sorted(keywords & body_words)
    all_matches = sorted(set(title_matches) | set(body_matches))

    if not keywords:
        category = "Not assessed"
        explanation = "The question needs more specific search terms."
    elif not all_matches:
        category = "Weakly related"
        explanation = (
            "No significant keywords from the research question "
            "were found in the available record text."
        )
    elif title_matches and body_matches:
        category = "Potentially directly relevant"
        explanation = (
            "The record matches the research topic in both its "
            "title and supporting text. Its actual relevance "
            "still needs checking."
        )
    else:
        category = "Related"
        explanation = (
            "The record mentions the research topic, but keyword "
            "matching alone cannot establish whether it answers "
            "the question."
        )

    return {
        "category": category,
        "explanation": explanation,
        "matched_keywords": all_matches,
        "verified": False,
    }


if __name__ == "__main__":
    question = (
        "What action has the UK Parliament taken "
        "to address homelessness since 2020?"
    )

    examples = [
        {
            "title": "Homelessness policy",
            "answer": "The department described homelessness prevention funding."
        },
        {
            "title": "Social housing",
            "answer": "The report discusses housing availability."
        },
        {
            "title": "Temporary accommodation and pets",
            "answer": "The guidance discusses pet-friendly accommodation."
        },
    ]

    for record in examples:
        result = assess_evidence(question, record)
        print(f"{record['title']}: {result['category']}")
        print(f"  {result['explanation']}")
        print()
