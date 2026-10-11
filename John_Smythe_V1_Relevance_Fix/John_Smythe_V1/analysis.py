
"""
JOHN SMYTHE RESEARCH ENGINE
Research Analysis Module — Version 0.1

Organises research evidence, constructs timelines,
flags potentially conflicting claims and prepares reports.

AI integration will be added later.

IMPORTANT:
This module does not independently verify factual claims.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


class ResearchAnalysis:

    def __init__(self, question):
        self.question = question
        self.evidence = []
        self.findings = []
        self.limitations = []

    def add_evidence(
        self,
        title,
        source,
        date=None,
        statement=None,
        url=None,
        reference=None,
    ):
        """Add an evidence record to the investigation."""

        record = {
            "id": len(self.evidence) + 1,
            "title": title,
            "source": source,
            "date": date,
            "statement": statement,
            "url": url,
            "reference": reference,
            "verified": False,
        }

        self.evidence.append(record)
        return record

    def build_timeline(self):
        """Sort dated evidence into chronological order."""

        dated = [
            item for item in self.evidence
            if item.get("date")
        ]

        def date_key(item):
            try:
                return datetime.fromisoformat(
                    item["date"].replace("Z", "+00:00")
                ).timestamp()
            except (ValueError, TypeError, OverflowError):
                return float("inf")

        return sorted(dated, key=date_key)

    def add_finding(self, finding, evidence_ids=None):
        """Record a research finding with evidence references."""

        record = {
            "finding": finding,
            "evidence_ids": evidence_ids or [],
            "status": "Requires verification",
        }

        self.findings.append(record)
        return record

    def add_limitation(self, description):
        """Record missing information or research limitations."""
        self.limitations.append(description)

    def flag_possible_conflicts(self):
        """
        Flag records with the same title but different statements.

        These are only potential differences, not confirmed
        contradictions. Human or AI review is required.
        """

        conflicts = []

        for index, first in enumerate(self.evidence):
            for second in self.evidence[index + 1:]:

                same_title = (
                    first["title"].strip().lower()
                    == second["title"].strip().lower()
                )

                different_statement = (
                    first.get("statement")
                    and second.get("statement")
                    and first["statement"] != second["statement"]
                )

                if same_title and different_statement:
                    conflicts.append({
                        "first_id": first["id"],
                        "second_id": second["id"],
                        "status": "Possible difference — review required",
                    })

        return conflicts

    def generate_report(self):
        """Create a structured research report."""

        return {
            "project": "John Smythe Research Engine",
            "question": self.question,
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "verification_status": "Not independently verified",
            "evidence_count": len(self.evidence),
            "timeline": self.build_timeline(),
            "evidence": self.evidence,
            "findings": self.findings,
            "possible_conflicts": self.flag_possible_conflicts(),
            "limitations": self.limitations,
        }

    def export_report(self, filename="analysis-report.json"):
        """Save the research report as a JSON file."""

        report = self.generate_report()

        path = Path(filename)

        with path.open("w", encoding="utf-8") as file:
            json.dump(
                report,
                file,
                indent=2,
                ensure_ascii=False,
            )

        return path


if __name__ == "__main__":

    research = ResearchAnalysis(
        "What immigration policies has the UK introduced since 2010?"
    )

    research.add_limitation(
        "Live documents have not yet been retrieved or reviewed."
    )

    research.add_limitation(
        "AI analysis has not yet been enabled."
    )

    research.export_report()

    print("John Smythe Research Analysis initialized.")
    print("Evidence records:", len(research.evidence))
    print("Report created: analysis-report.json")
