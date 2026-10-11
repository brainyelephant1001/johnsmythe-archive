
"""
JOHN SMYTHE — SOURCECHECK
Version 0.1

Records research sources, references, publication dates,
verification status and supporting evidence.

This module does not independently verify claims yet.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


class SourceCheck:

    def __init__(self):
        self.sources = []

    def add_source(
        self,
        title,
        url,
        publisher,
        publication_date=None,
        reference=None,
        evidence=None,
    ):
        """Register a source for later verification."""

        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("A valid source URL is required.")

        source = {
            "id": len(self.sources) + 1,
            "title": title,
            "url": url,
            "publisher": publisher,
            "publication_date": publication_date,
            "reference": reference,
            "evidence": evidence,
            "verification_status": "Not independently verified",
            "checked_at": None,
            "added_at": datetime.now(timezone.utc).isoformat(),
        }

        self.sources.append(source)
        return source

    def list_sources(self):
        """Return all recorded sources."""
        return self.sources

    def find_by_publisher(self, publisher):
        """Find sources from a particular publisher."""
        return [
            source for source in self.sources
            if source["publisher"].lower() == publisher.lower()
        ]

    def summary(self):
        """Generate a basic source summary."""
        return {
            "total_sources": len(self.sources),
            "verified_sources": sum(
                source["verification_status"] == "Verified"
                for source in self.sources
            ),
            "pending_verification": sum(
                source["verification_status"] != "Verified"
                for source in self.sources
            ),
        }

    def export(self, filename="sourcecheck-results.json"):
        """Save recorded sources to a JSON file."""

        output = {
            "system": "John Smythe SourceCheck",
            "created": datetime.now(timezone.utc).isoformat(),
            "summary": self.summary(),
            "sources": self.sources,
        }

        path = Path(filename)

        with path.open("w", encoding="utf-8") as file:
            json.dump(output, file, indent=2, ensure_ascii=False)

        return path


if __name__ == "__main__":

    checker = SourceCheck()

    checker.add_source(
        title="UK Parliament",
        url="https://www.parliament.uk/",
        publisher="UK Parliament",
        evidence="Official parliamentary website",
    )

    checker.export()

    print("SourceCheck initialized.")
    print(checker.summary())
