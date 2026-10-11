
"""
John Smythe Research Engine
Evidence Assessment - Version 0.2 (Revised)

Separates:
- Research relevance
- Questions and allegations
- Source responses
- Reported outcomes
- Evidence limitations

This is a rule-based prototype, not a fact-checker.
All findings require verification against original sources.
"""

import re

from evidence_assessment import assess_evidence


def clean_text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def find_statements(text, patterns):
    if not text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", text)

    return [
        sentence.strip()
        for sentence in sentences
        if any(
            re.search(pattern, sentence, re.IGNORECASE)
            for pattern in patterns
        )
    ]


ANNOUNCEMENT_PATTERNS = [
    r"\bannounc(?:ed|ement|es|ing)\b",
    r"\bplans? to\b",
    r"\bpropos(?:ed|al|es)\b",
    r"\bcommitt(?:ed|ment)\b",
]

OUTCOME_PATTERNS = [
    r"\breduc(?:ed|tion|ing)\b",
    r"\bincreas(?:ed|e|ing)\b",
    r"\bimprov(?:ed|ement|ing)\b",
    r"\bdeclin(?:ed|e|ing)\b",
    r"\bmeasur(?:ed|ement)\b",
]

LIMITATION_PATTERNS = [
    r"\bno evidence\b",
    r"\binsufficient evidence\b",
    r"\bnot (?:yet )?(?:known|established|verified)\b",
    r"\bno data\b",
    r"\bdata (?:is|are) unavailable\b",
    r"\bdoes not hold (?:the )?(?:data|evidence|information)\b",
]


def assess_record(question, record):
    relevance = assess_evidence(question, record)

    parliamentary_question = clean_text(
        record.get("question")
    )

    source_answer = clean_text(
        record.get("answer")
    )

    source_content = clean_text(
        record.get("content")
    )

    description = clean_text(
        record.get("description")
    )

    # Questions are not treated as evidence of their claims.
    # Prefer actual answers or document content.
    if source_answer:
        evidence_text = source_answer
        evidence_type = "Source answer"
    elif source_content:
        evidence_text = source_content
        evidence_type = "Source document content"
    elif description:
        evidence_text = description
        evidence_type = "Source description only"
    else:
        evidence_text = ""
        evidence_type = "No substantive evidence text"

    announcements = find_statements(
        evidence_text,
        ANNOUNCEMENT_PATTERNS,
    )

    outcomes = find_statements(
        evidence_text,
        OUTCOME_PATTERNS,
    )

    limitations = find_statements(
        evidence_text,
        LIMITATION_PATTERNS,
    )

    observations = []

    if parliamentary_question:
        observations.append(
            "A parliamentary question is present. "
            "Its wording is not treated as a verified claim."
        )

    if evidence_type == "Source description only":
        observations.append(
            "Only a source description is available. "
            "The underlying document has not been examined."
        )

    if evidence_type == "No substantive evidence text":
        observations.append(
            "No answer, document content or description "
            "is available for substantive assessment."
        )

    if announcements:
        observations.append(
            "The source response contains announcement "
            "or proposal language."
        )

    if outcomes:
        observations.append(
            "The source response mentions a change or outcome. "
            "The figures and causes remain unverified."
        )

    if limitations:
        observations.append(
            "The source response contains language indicating "
            "missing or uncertain evidence."
        )

    if limitations:
        conclusion = (
            "The available source response identifies an "
            "evidence limitation. Its scope and accuracy "
            "require checking against the original source."
        )
    elif outcomes:
        conclusion = (
            "The available source response mentions an outcome "
            "or change. This module cannot establish whether "
            "the claim is accurate or what caused it."
        )
    elif announcements:
        conclusion = (
            "The available source response mentions an "
            "announcement or proposal. This does not prove "
            "implementation or effectiveness."
        )
    else:
        conclusion = (
            "The available text does not establish a "
            "verifiable research conclusion."
        )

    return {
        "relevance": relevance["category"],
        "relevance_explanation": relevance["explanation"],
        "matched_keywords": relevance["matched_keywords"],
        "evidence_type": evidence_type,
        "question_text": parliamentary_question,
        "source_response_text": evidence_text,
        "question_is_evidence": False,
        "observations": observations,
        "announcement_passages": announcements,
        "outcome_passages": outcomes,
        "limitation_passages": limitations,
        "conclusion": conclusion,
        "verified": False,
    }


if __name__ == "__main__":
    question = "Has homelessness policy reduced homelessness?"

    examples = [
        {
            "title": "Parliamentary homelessness question",
            "question": (
                "Has homelessness increased by 20 percent "
                "because of government policy?"
            ),
            "answer": (
                "The department does not hold evidence "
                "supporting that claim."
            ),
        },
        {
            "title": "Homelessness statistics",
            "answer": (
                "The report states that homelessness increased "
                "during the reporting period."
            ),
        },
        {
            "title": "Housing announcement",
            "answer": (
                "The department announced plans to build "
                "additional homes."
            ),
        },
        {
            "title": "Parliamentary question without answer",
            "question": (
                "Why has homelessness increased "
                "by 30 percent?"
            ),
        },
    ]

    for number, record in enumerate(examples, 1):
        result = assess_record(question, record)

        print("\n" + "=" * 55)
        print("TEST:", number)
        print("RECORD:", record["title"])
        print("EVIDENCE TYPE:", result["evidence_type"])
        print("QUESTION IS EVIDENCE:", result["question_is_evidence"])
        print("SOURCE TEXT:", result["source_response_text"])
        print("ASSESSMENT:", result["conclusion"])
        print("VERIFIED:", result["verified"])
