
"""
JOHN SMYTHE RESEARCH ENGINE
Search Intelligence — Version 0.1

Converts natural-language research questions into
search terms for public-record databases.

No AI service or paid API is required.
"""

import re


STOP_WORDS = {
    "a", "an", "the", "and", "or", "but",
    "is", "are", "was", "were", "be", "been",
    "to", "of", "for", "from", "by", "with",
    "in", "on", "at", "as", "it", "its",
    "what", "when", "where", "why", "who",
    "which", "how", "has", "have", "had",
    "does", "did", "do", "can", "could",
    "would", "should", "since", "between",
    "during", "over", "under", "about",
    "changed", "change", "changes",
    "uk", "britain", "british", "government"
}


def extract_keywords(question):
    """Identify meaningful search terms."""

    question = str(question).lower()

    words = re.findall(
        r"[a-z]+(?:'[a-z]+)?|\d{4}",
        question
    )

    keywords = []

    for word in words:

        if word in STOP_WORDS:
            continue

        if len(word) < 3 and not word.isdigit():
            continue

        if word not in keywords:
            keywords.append(word)

    return keywords


def extract_years(question):
    """Find four-digit years in the research question."""

    years = re.findall(
        r"\b(?:19|20)\d{2}\b",
        str(question)
    )

    return list(dict.fromkeys(years))


def generate_search_terms(question):
    """
    Generate progressively broader search terms.

    The original question is preserved for reporting.
    """

    keywords = extract_keywords(question)
    years = extract_years(question)

    terms = []

    if keywords:

        # Subject terms without years.
        subjects = [
            word for word in keywords
            if word not in years
        ]

        if subjects:
            terms.append(" ".join(subjects[:4]))

            # Broader fallback searches.
            terms.append(" ".join(subjects[:2]))
            terms.append(subjects[0])

    # Include the original question as a fallback.
    if not terms:
        terms.append(str(question).strip())

    # Remove duplicate searches.
    terms = list(dict.fromkeys(
        term for term in terms if term.strip()
    ))

    return {
        "original_question": question,
        "keywords": keywords,
        "years": years,
        "search_terms": terms,
    }


if __name__ == "__main__":

    print("JOHN SMYTHE — SEARCH INTELLIGENCE")

    question = input(
        "\nEnter a research question:\n> "
    )

    result = generate_search_terms(question)

    print("\nExtracted keywords:")
    print(result["keywords"])

    print("\nYears identified:")
    print(result["years"])

    print("\nSuggested searches:")
    for term in result["search_terms"]:
        print("-", term)
