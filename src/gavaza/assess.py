"""POPIA compliance assessment engine.

An :class:`Assessment` records an answer (``yes``, ``no`` or ``partial``) plus
an optional note for every checklist item across the eight conditions, and
computes per-condition scores (0-100), an overall score and an A-F grade.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from gavaza import __version__
from gavaza.conditions import CONDITION_MAP, ChecklistItem, item_lookup
from gavaza.config import Company

ANSWER_VALUES = ("yes", "no", "partial")
ANSWER_SCORES = {"yes": 100.0, "partial": 50.0, "no": 0.0}

GRADE_THRESHOLDS: tuple[tuple[str, float], ...] = (
    ("A", 90.0),
    ("B", 80.0),
    ("C", 70.0),
    ("D", 60.0),
    ("E", 50.0),
    ("F", 0.0),
)


def grade_for(score: float) -> str:
    """Map a 0-100 score to an A-F grade (A >= 90, B >= 80, ... F < 50)."""
    for grade, threshold in GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return "F"


def maturity_level(score: float) -> int:
    """Map a 0-100 score to a 1-5 maturity level.

    Levels: 1 (score < 50), 2 (50-69), 3 (70-79), 4 (80-89), 5 (90+).
    """
    if score >= 90.0:
        return 5
    if score >= 80.0:
        return 4
    if score >= 70.0:
        return 3
    if score >= 50.0:
        return 2
    return 1


MATURITY_LABELS: dict[int, str] = {
    1: "Ad hoc",
    2: "Developing",
    3: "Established",
    4: "Managed",
    5: "Optimising",
}


def maturity_label(level: int) -> str:
    """Return the human label for a maturity level."""
    return MATURITY_LABELS[level]


@dataclass
class Answer:
    """A single answer to a checklist question."""

    value: str
    note: str = ""

    @classmethod
    def from_raw(cls, raw: Any) -> Answer:
        """Coerce a raw value (string or dict) into an Answer."""
        if isinstance(raw, dict):
            value = str(raw.get("value", "no")).lower()
            note = str(raw.get("note", ""))
        else:
            value = str(raw).lower()
            note = ""
        if value not in ANSWER_VALUES:
            raise ValueError(f"invalid answer value {value!r}; expected yes, no or partial")
        return cls(value=value, note=note)

    @property
    def score(self) -> float:
        """The numeric score contribution of this answer (0, 50 or 100)."""
        return ANSWER_SCORES[self.value]

    def to_dict(self) -> dict[str, str]:
        """JSON-serialisable representation."""
        return asdict(self)


class Assessment:
    """Answers to the full questionnaire plus scoring helpers."""

    def __init__(
        self,
        company: Company,
        answers: dict[str, Answer] | None = None,
        weights: dict[str, float] | None = None,
    ) -> None:
        self.company = company
        self.answers: dict[str, Answer] = answers if answers is not None else {}
        self._lookup = item_lookup()
        self._weights: dict[str, float] = dict(weights) if weights else {
            slug: 1.0 for slug in CONDITION_MAP
        }

    def weight(self, slug: str) -> float:
        """Return the scoring weight of one condition."""
        return self._weights.get(slug, 1.0)

    def set_weight(self, slug: str, weight: float) -> None:
        """Set the scoring weight of one condition.

        Raises:
            KeyError: when the slug is unknown.
            ValueError: when the weight is negative.
        """
        if slug not in CONDITION_MAP:
            raise KeyError(f"unknown condition slug: {slug}")
        if weight < 0:
            raise ValueError("condition weight must be zero or positive")
        self._weights[slug] = float(weight)

    # -- answering ---------------------------------------------------------

    def answer(self, item_id: str, value: str, note: str = "") -> Answer:
        """Record an answer for a checklist item, validating the item id."""
        if item_id not in self._lookup:
            raise KeyError(f"unknown checklist item id: {item_id}")
        answer = Answer.from_raw({"value": value, "note": note})
        self.answers[item_id] = answer
        return answer

    def answered_items(self) -> list[tuple[str, str, ChecklistItem, Answer]]:
        """Return (condition slug, condition name, item, answer) for all answers."""
        return [
            (slug, CONDITION_MAP[slug].name, item, self.answers[item.id])
            for item_id, (slug, _name, item) in self._lookup.items()
            if item_id in self.answers
        ]

    # -- scoring -----------------------------------------------------------

    def condition_score(self, slug: str) -> float:
        """Compute the 0-100 score for one condition (mean of its answers)."""
        condition = CONDITION_MAP[slug]
        scores = [self.answers[i].score for i in condition.checklist_ids if i in self.answers]
        if not scores:
            return 0.0
        return round(sum(scores) / len(scores), 1)

    def condition_scores(self) -> dict[str, float]:
        """Return {condition slug: score} for all eight conditions."""
        return {slug: self.condition_score(slug) for slug in CONDITION_MAP}

    def overall_score(self) -> float:
        """Overall score: the weighted mean of the per-condition scores.

        Conditions with weight 0 drop out of the calculation entirely.
        The default weight of every condition is 1.0, which makes the
        overall score a plain mean.
        """
        total_weight = sum(self.weight(slug) for slug in CONDITION_MAP)
        if total_weight <= 0:
            return 0.0
        weighted = sum(
            self.condition_score(slug) * self.weight(slug) for slug in CONDITION_MAP
        )
        return round(weighted / total_weight, 1)

    def grade(self) -> str:
        """Overall A-F grade."""
        return grade_for(self.overall_score())

    def condition_maturity(self, slug: str) -> int:
        """Maturity level (1-5) of one condition."""
        return maturity_level(self.condition_score(slug))

    def overall_maturity(self) -> int:
        """Maturity level (1-5) of the overall assessment."""
        return maturity_level(self.overall_score())

    def gap_summary(self) -> list[dict[str, Any]]:
        """Per-condition rows with score, maturity, and coverage counts."""
        rows: list[dict[str, Any]] = []
        for slug, condition in CONDITION_MAP.items():
            answered = sum(
                1 for item_id in condition.checklist_ids if item_id in self.answers
            )
            rows.append(
                {
                    "slug": slug,
                    "name": condition.name,
                    "score": self.condition_score(slug),
                    "maturity": self.condition_maturity(slug),
                    "answered": answered,
                    "total": len(condition.checklist_ids),
                }
            )
        return rows

    # -- remediation -------------------------------------------------------

    def remediation_items(self) -> list[dict[str, Any]]:
        """Prioritised remediation list (worst-scoring conditions first).

        Only items answered ``no`` or ``partial`` are included. Within a
        condition, items are listed in checklist order.
        """
        ordered = sorted(
            CONDITION_MAP.values(), key=lambda c: (self.condition_score(c.slug), c.slug)
        )
        items: list[dict[str, Any]] = []
        for condition in ordered:
            for item in condition.checklist:
                answer = self.answers.get(item.id)
                if answer is None or answer.value == "yes":
                    continue
                items.append(
                    {
                        "condition": condition.name,
                        "condition_slug": condition.slug,
                        "condition_score": self.condition_score(condition.slug),
                        "item_id": item.id,
                        "question": item.question,
                        "answer": answer.value,
                        "note": answer.note,
                        "remediation": item.remediation,
                    }
                )
        return items

    # -- serialisation -----------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Full JSON-serialisable representation of the assessment."""
        conditions = []
        for slug, condition in CONDITION_MAP.items():
            answers = []
            for item in condition.checklist:
                answer = self.answers.get(item.id)
                answers.append(
                    {
                        "id": item.id,
                        "question": item.question,
                        "value": answer.value if answer else "unanswered",
                        "note": answer.note if answer else "",
                    }
                )
            conditions.append(
                {
                    "slug": slug,
                    "name": condition.name,
                    "act_reference": condition.act_reference,
                    "description": condition.description,
                    "weight": self.weight(slug),
                    "score": self.condition_score(slug),
                    "maturity": self.condition_maturity(slug),
                    "answers": answers,
                }
            )
        return {
            "version": __version__,
            "company": self.company.name,
            "date": datetime.now(UTC).date().isoformat(),
            "overall_score": self.overall_score(),
            "grade": self.grade(),
            "overall_maturity": self.overall_maturity(),
            "conditions": conditions,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any], company: Company | None = None) -> Assessment:
        """Rebuild an Assessment from a saved results dictionary."""
        source = company or Company(name=str(data.get("company", "")))
        assessment = cls(source)
        for condition in data.get("conditions", []):
            slug = condition.get("slug")
            if slug in CONDITION_MAP and condition.get("weight") is not None:
                assessment.set_weight(slug, float(condition["weight"]))
            for answer in condition.get("answers", []):
                item_id = answer.get("id")
                value = answer.get("value")
                if item_id and value in ANSWER_VALUES:
                    assessment.answer(item_id, value, note=str(answer.get("note", "")))
        return assessment


def save_results(assessment: Assessment, path: Path) -> Path:
    """Write the assessment results to JSON and return the path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(assessment.to_dict(), handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return path


def load_results(path: Path, company: Company | None = None) -> Assessment:
    """Load an Assessment from a saved results JSON file."""
    with path.open("r", encoding="utf-8") as handle:
        return Assessment.from_dict(json.load(handle), company=company)


def run_interactive(
    company: Company, prompt: Callable[[str], str] | None = None
) -> Assessment:
    """Run the questionnaire interactively, prompting for every checklist item.

    ``prompt`` defaults to :func:`input`; tests may inject a scripted prompt.
    Valid answers are ``yes``, ``no`` and ``partial`` (with an optional note).
    """
    ask = prompt or input
    assessment = Assessment(company)
    total = len(item_lookup())
    for index, (item_id, (slug, condition_name, item)) in enumerate(item_lookup().items(), 1):
        question = (
            f"[{index}/{total}] {condition_name} ({slug}) — {item.question}\n"
            "Answer (yes/no/partial, or 's' to skip): "
        )
        while True:
            raw = ask(question).strip().lower()
            if raw in ("s", "skip", ""):
                break
            if raw in ANSWER_VALUES:
                note = ""
                if raw in ("no", "partial"):
                    note = ask("  Note (optional): ").strip()
                assessment.answer(item_id, raw, note)
                break
            print("  Please enter 'yes', 'no' or 'partial' (or 's' to skip).")
    return assessment
