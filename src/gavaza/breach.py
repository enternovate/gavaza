"""Breach register (CSV) and the 72-hour breach notification guide.

POPIA section 22 requires the responsible party to notify the Information
Regulator and, in certain circumstances, affected data subjects, without
undue delay after becoming aware of a security compromise. This module
maintains the breach register CSV and prints the notification checklist.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

BREACH_HEADER = [
    "date",
    "description",
    "categories",
    "affected_count",
    "risk_assessment",
    "notification_status",
]

BREACH_FILENAME = "breach-register.csv"


@dataclass
class BreachRecord:
    """A single entry in the breach register."""

    date: str = field(default_factory=lambda: datetime.now(UTC).date().isoformat())
    description: str = ""
    categories: str = ""
    affected_count: int | str = 0
    risk_assessment: str = ""
    notification_status: str = "not notified"

    def to_row(self) -> list[str]:
        """The CSV row for this record, in header order."""
        return [
            self.date,
            self.description,
            self.categories,
            str(self.affected_count),
            self.risk_assessment,
            self.notification_status,
        ]

    @classmethod
    def from_row(cls, row: list[str]) -> BreachRecord:
        """Build a record from a CSV row in header order."""
        padded = (row + [""] * len(BREACH_HEADER))[: len(BREACH_HEADER)]
        return cls(*padded)


def register_path(home: Path | None = None) -> Path:
    """Return the path of the breach register CSV in the data directory."""
    from gavaza.config import data_dir

    return (home or data_dir()) / BREACH_FILENAME


def ensure_register(path: Path | None = None) -> Path:
    """Create the breach register CSV with its header if it does not exist."""
    target = path or register_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        with target.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(BREACH_HEADER)
    return target


def add_breach(
    record: BreachRecord, path: Path | None = None
) -> Path:
    """Append a breach record to the register and return the register path."""
    target = ensure_register(path)
    with target.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(record.to_row())
    return target


def list_breaches(path: Path | None = None) -> list[BreachRecord]:
    """Read all breach records from the register."""
    target = ensure_register(path)
    with target.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    if not rows or rows[0] != BREACH_HEADER:
        raise ValueError(f"{target} is not a valid Gavaza breach register")
    return [BreachRecord.from_row(row) for row in rows[1:] if any(row)]


def notification_timeline() -> list[dict[str, str]]:
    """The breach notification timeline guide (section 22 duties)."""
    return [
        {
            "when": "Immediately (0 hours)",
            "action": (
                "Contain the breach, preserve evidence, and assemble the incident "
                "response team. Identify what happened, when and how."
            ),
        },
        {
            "when": "Within 72 hours",
            "action": (
                "Notify the Information Regulator in writing with: a description of "
                "the breach; the categories of personal information involved; the "
                "number of data subjects affected; the measures taken or proposed to "
                "address the breach; and the identity of the Information Officer."
            ),
        },
        {
            "when": "Without undue delay (if harm is likely)",
            "action": (
                "Notify affected data subjects if the breach is likely to result in "
                "substantial harm or inconvenience to them (section 22(4)), using "
                "contact details held for them."
            ),
        },
        {
            "when": "At the same time",
            "action": (
                "Log the breach in the breach register: date, description, categories, "
                "affected count, risk assessment and notification status."
            ),
        },
        {
            "when": "Ongoing",
            "action": (
                "Monitor the response, document corrective actions, and update the "
                "register when the notification status changes."
            ),
        },
    ]


def notification_checklist() -> list[str]:
    """The 72-hour notification checklist printed when a breach is logged."""
    return [
        "Contain the breach and preserve evidence.",
        "Identify the categories of personal information involved.",
        "Determine the number of affected data subjects.",
        "Assess the risk of harm to data subjects.",
        "Notify the Information Regulator within 72 hours (section 22).",
        "Notify affected data subjects if substantial harm is likely.",
        "Record the breach in the breach register.",
        "Document corrective and preventive measures.",
    ]


def parse_affected(value: Any) -> int:
    """Parse the affected count, raising ValueError for non-integers."""
    return int(value)


def records_to_dicts(records: list[BreachRecord]) -> list[dict[str, str]]:
    """Convert records to plain dictionaries for display or reporting."""
    return [dict(zip(BREACH_HEADER, record.to_row())) for record in records]
