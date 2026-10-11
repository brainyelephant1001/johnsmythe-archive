"""Shared, conservative topic matching for source discovery. No legal conclusions."""
import re

FILLER = set("what which when where why how the and for from with about against available protects protect legal law laws legislation rights remedies consumer consumers contract contracts unfair breaches breach does do did can are were was uk united kingdom government action steps taken regarding relevant explain identify find give me of in to on a an is under".split())

def words(text):
    return set(re.findall(r"[a-z]{3,}", str(text).lower()))

def topic(question):
    q = str(question).lower()
    if any(w in q for w in ("telecom", "mobile phone", "broadband", "phone contract", "o2 ", "mis-selling")) and any(w in q for w in ("consumer", "contract", "mis-sell", "misrepresent", "unfair", "rights")):
        return "telecom_consumer"
    return "general"

def focus_words(question):
    return words(question) - FILLER


def government_queries(question):
    question = str(question).strip()

    if topic(question) == "telecom_consumer":
        return [
            "telecoms consumer contracts Ofcom",
            "unfair consumer contract terms"
        ]

    # Search for a complete Act title first.
    match = re.search(
        r"\b([A-Za-z][A-Za-z,\s-]*?\s+Act\s+\d{4})\b",
        question,
        flags=re.IGNORECASE
    )

    if match:
        return [match.group(1).strip()]

    # General research queries.
    key = sorted(
        focus_words(question),
        key=lambda x: (-len(x), x)
    )

    return [" ".join(key[:4])] if key else []


def government_score(question, title, description):
    title = str(title or "")
    description = str(description or "")

    text = words(title + " " + description)
    heading = words(title)

    if topic(question) == "telecom_consumer":
        telecom = bool(text & {
            "telecoms", "telecommunications", "broadband",
            "mobile", "phone", "phones", "ofcom"
        })

        consumer_law = bool(text & {
            "consumer", "consumers", "contract", "contracts",
            "unfair", "misrepresentation", "misleading",
            "selling", "terms"
        })

        general_law = (
            bool(heading & {
                "unfair", "consumer", "consumers",
                "contracts", "contract"
            })
            and bool(text & {
                "terms", "fair", "rights", "protection"
            })
        )

        if not ((telecom and consumer_law) or general_law):
            return 0

        return (
            5 * len(heading & {
                "telecoms", "telecommunications", "broadband",
                "ofcom", "consumer", "consumers", "unfair",
                "contract", "contracts"
            })
            + len(text & {
                "misrepresentation", "misleading", "selling",
                "terms", "rights", "protection"
            })
            + 1
        )

    # Give priority to documents mentioning a named Act.
    match = re.search(
        r"\b([A-Za-z][A-Za-z,\s-]*?\s+Act\s+\d{4})\b",
        str(question),
        flags=re.IGNORECASE
    )

    if match:
        exact_title = " ".join(match.group(1).lower().split())
        combined = " ".join(
            (title + " " + description).lower().split()
        )

        if exact_title in title.lower():
            return 100

        if exact_title in combined:
            return 70

        return 0

    # General topic relevance scoring.
    focus = focus_words(question)
    matches = text & focus

    if not focus or len(matches) < (1 if len(focus) == 1 else 2):
        return 0

    return 4 * len(heading & focus) + len(matches)


# Targeted discovery only: no assertion that an Act applies to any specific case.
TELECOM_ACT_TITLES = [
    "Consumer Rights Act 2015",
    "Misrepresentation Act 1967",
    "Communications Act 2003",
    "Digital Markets, Competition and Consumers Act 2024",
]

def legislation_queries(question):
    question = str(question).strip()

    if topic(question) == "telecom_consumer":
        return TELECOM_ACT_TITLES

    # Recognise complete Act titles, including their year.
    match = re.search(
        r"\b([A-Za-z][A-Za-z,\s-]*?\s+Act\s+\d{4})\b",
        question,
        flags=re.IGNORECASE
    )

    if match:
        return [match.group(1).strip()]

    # Preserve broader research searches.
    focus = sorted(
        focus_words(question),
        key=lambda x: (-len(x), x)
    )

    return focus[:2]


def legislation_score(question, title, search_term):
    title_lower = " ".join(str(title).lower().split())
    search_lower = " ".join(str(search_term).lower().split())

    # Preserve the specialist telecommunications searches.
    if topic(question) == "telecom_consumer":
        return 100 if title_lower == search_lower else 0

    # Give exact legislation titles highest priority.
    if re.search(r"\bact\s+\d{4}\b", search_lower):
        if title_lower == search_lower:
            return 100

        if search_lower in title_lower:
            return 90

        return 0

    # General topical legislation searches.
    focus = focus_words(question)
    matches = words(title) & focus

    if len(matches) < (1 if len(focus) == 1 else 2):
        return 0

    return len(matches) * 3

def research_guidance(question):
    """Transparent starting points, not findings or a legal opinion."""
    if topic(question) != "telecom_consumer":
        return None
    return {
        "heading": "Legal avenues to investigate",
        "notice": "These are suggested starting points, not retrieved or verified findings. Check current law, commencement, jurisdiction, contract dates and your circumstances.",
        "topics": [
            {"name": "Consumer Rights Act 2015", "why": "Check whether the contract terms are unfair and which consumer protections apply.", "url": "https://www.legislation.gov.uk/ukpga/2015/15/contents"},
            {"name": "Misrepresentation Act 1967", "why": "Examine remedies where a false statement induced a contract.", "url": "https://www.legislation.gov.uk/ukpga/1967/7/contents"},
            {"name": "Communications Act 2003", "why": "Check the framework for communications regulation and Ofcom's powers.", "url": "https://www.legislation.gov.uk/ukpga/2003/21/contents"},
            {"name": "Ofcom consumer protections", "why": "Check the applicable General Conditions, complaint procedures and ADR options.", "url": "https://www.ofcom.org.uk/"},
        ],
        "next_steps": "Possible routes to examine include a formal provider complaint, ADR where eligible, and civil remedies where a legal basis exists. No outcome or entitlement has been assessed."
    }
