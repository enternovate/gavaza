"""Tests for the assessment engine: scoring math, grades and remediation."""

from __future__ import annotations

import pytest

from gavaza.assess import Assessment, grade_for, run_interactive
from gavaza.conditions import ALL_ITEM_IDS, CONDITION_MAP
from gavaza.config import Company


@pytest.fixture
def company() -> Company:
    return Company(name="Test Co")


@pytest.fixture
def all_yes(company: Company) -> Assessment:
    assessment = Assessment(company)
    for item_id in ALL_ITEM_IDS:
        assessment.answer(item_id, "yes")
    return assessment


def test_all_yes_scores_100_grade_a(all_yes: Assessment) -> None:
    assert all_yes.overall_score() == 100.0
    assert all_yes.grade() == "A"
    for slug in CONDITION_MAP:
        assert all_yes.condition_score(slug) == 100.0


def test_all_no_scores_zero_grade_f(company: Company) -> None:
    assessment = Assessment(company)
    for item_id in ALL_ITEM_IDS:
        assessment.answer(item_id, "no")
    assert assessment.overall_score() == 0.0
    assert assessment.grade() == "F"


def test_all_partial_scores_50(company: Company) -> None:
    assessment = Assessment(company)
    for item_id in ALL_ITEM_IDS:
        assessment.answer(item_id, "partial")
    assert assessment.overall_score() == 50.0
    assert assessment.grade() == "E"


def test_condition_score_math(company: Company) -> None:
    """A condition's score is the mean of its item scores."""
    assessment = Assessment(company)
    # Accountability has 5 items: 3 yes (100), 1 partial (50), 1 no (0).
    ids = CONDITION_MAP["accountability"].checklist_ids
    assert len(ids) == 5
    for index, item_id in enumerate(ids):
        value = "yes" if index < 3 else ("partial" if index == 3 else "no")
        assessment.answer(item_id, value)
    assert assessment.condition_score("accountability") == 70.0


def test_mixed_overall_and_grade(company: Company) -> None:
    """Half the conditions answered yes, half unanswered -> overall 50, grade E."""
    assessment = Assessment(company)
    for slug in list(CONDITION_MAP)[:4]:
        for item_id in CONDITION_MAP[slug].checklist_ids:
            assessment.answer(item_id, "yes")
    assert assessment.overall_score() == 50.0
    assert assessment.grade() == "E"


@pytest.mark.parametrize(
    ("score", "grade"),
    [(95.0, "A"), (90.0, "A"), (89.9, "B"), (79.9, "C"), (69.9, "D"), (59.9, "E"), (49.9, "F")],
)
def test_grade_thresholds(score: float, grade: str) -> None:
    assert grade_for(score) == grade


def test_remediation_prioritised(company: Company) -> None:
    """Remediation lists the failing condition first, worst conditions first."""
    assessment = Assessment(company)
    for slug in CONDITION_MAP:
        value = "no" if slug == "security_safeguards" else "yes"
        for item_id in CONDITION_MAP[slug].checklist_ids:
            assessment.answer(item_id, value)
    items = assessment.remediation_items()
    assert items
    assert all(item["condition_slug"] == "security_safeguards" for item in items)
    # A partial answer elsewhere still ranks below the worst condition.
    assessment.answer("ds-1", "partial", note="in progress")
    items = assessment.remediation_items()
    assert items[0]["condition_slug"] == "security_safeguards"
    assert any(item["item_id"] == "ds-1" and item["answer"] == "partial" for item in items)


def test_serialization_round_trip(company: Company) -> None:
    """to_dict -> from_dict preserves answers, notes and scores."""
    assessment = Assessment(company)
    assessment.answer("acc-1", "yes", note="registered with the Regulator")
    assessment.answer("ss-3", "no")
    data = assessment.to_dict()
    assert data["company"] == "Test Co"
    assert data["grade"] == assessment.grade()
    restored = Assessment.from_dict(data, company=company)
    assert restored.answers["acc-1"].note == "registered with the Regulator"
    assert restored.condition_score("accountability") == assessment.condition_score("accountability")
    assert restored.overall_score() == assessment.overall_score()


def test_interactive_questionnaire_with_scripted_prompts(company: Company) -> None:
    """A scripted prompt can drive the questionnaire to completion."""
    script = iter(["yes"] * len(ALL_ITEM_IDS))
    assessment = run_interactive(company, prompt=lambda _question: next(script))
    assert assessment.overall_score() == 100.0
    assert len(assessment.answers) == len(ALL_ITEM_IDS)


def test_unknown_item_id_raises(company: Company) -> None:
    assessment = Assessment(company)
    with pytest.raises(KeyError):
        assessment.answer("nope-99", "yes")
    with pytest.raises(ValueError):
        assessment.answer("acc-1", "maybe")
