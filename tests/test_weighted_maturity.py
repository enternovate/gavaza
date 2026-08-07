"""Tests for weighted scoring, maturity levels, and gap summaries."""

from __future__ import annotations

import pytest

from gavaza.assess import (
    Assessment,
    maturity_label,
    maturity_level,
)
from gavaza.cli import main
from gavaza.config import Company
from gavaza.conditions import CONDITION_MAP, ALL_ITEM_IDS


@pytest.fixture
def company() -> Company:
    """A minimal company for assessment tests."""
    return Company(name="Acme (Pty) Ltd")


def _answer_everything(assessment: Assessment, value: str) -> Assessment:
    """Answer every checklist item with the same value."""
    for item_id in ALL_ITEM_IDS:
        assessment.answer(item_id, value)
    return assessment


def test_weights_default_to_one(company: Company) -> None:
    """Every condition must start with weight 1.0."""
    assessment = Assessment(company)
    for slug in CONDITION_MAP:
        assert assessment.weight(slug) == 1.0


def test_weighted_overall_score(company: Company) -> None:
    """A heavy weight on one condition must move the overall score."""
    assessment = _answer_everything(Assessment(company), "yes")
    # Drop accountability to zero answers but give it weight 10.
    for item_id in CONDITION_MAP["accountability"].checklist_ids:
        assessment.answer(item_id, "no")
    assessment.set_weight("accountability", 10.0)
    plain = sum(
        assessment.condition_score(slug) for slug in CONDITION_MAP
    ) / len(CONDITION_MAP)
    weighted = assessment.overall_score()
    assert weighted < plain  # the heavy zero pulls the weighted score down
    # Weight 0 removes the condition from the overall score.
    assessment.set_weight("accountability", 0.0)
    assert assessment.overall_score() > weighted


def test_set_weight_validates(company: Company) -> None:
    """Unknown slugs and negative weights must be rejected."""
    assessment = Assessment(company)
    with pytest.raises(KeyError):
        assessment.set_weight("nope", 1.0)
    with pytest.raises(ValueError):
        assessment.set_weight("accountability", -1.0)


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (95.0, 5),
        (90.0, 5),
        (85.0, 4),
        (75.0, 3),
        (70.0, 3),
        (60.0, 2),
        (30.0, 1),
        (0.0, 1),
    ],
)
def test_maturity_level_thresholds(score: float, expected: int) -> None:
    """Maturity levels must map scores to 1-5."""
    assert maturity_level(score) == expected


def test_maturity_labels() -> None:
    """Every maturity level must have a label."""
    assert maturity_label(5) == "Optimising"
    assert maturity_label(1) == "Ad hoc"


def test_gap_summary_shape(company: Company) -> None:
    """The gap summary must report one row per condition."""
    assessment = Assessment(company)
    for item_id in CONDITION_MAP["accountability"].checklist_ids:
        assessment.answer(item_id, "yes")
    rows = assessment.gap_summary()
    assert len(rows) == len(CONDITION_MAP)
    accountability = next(row for row in rows if row["slug"] == "accountability")
    assert accountability["answered"] == len(
        CONDITION_MAP["accountability"].checklist_ids
    )
    assert accountability["total"] == len(CONDITION_MAP["accountability"].checklist_ids)
    assert accountability["score"] == 100.0
    assert accountability["maturity"] == 5
    other = next(row for row in rows if row["slug"] != "accountability")
    assert other["answered"] == 0


def test_weights_survive_serialization(company: Company) -> None:
    """Weights must round-trip through to_dict and from_dict."""
    assessment = Assessment(company)
    assessment.set_weight("accountability", 2.5)
    restored = Assessment.from_dict(assessment.to_dict(), company=company)
    assert restored.weight("accountability") == 2.5
    assert restored.overall_score() == assessment.overall_score()


def test_to_dict_has_maturity(company: Company) -> None:
    """The serialized assessment must carry maturity data."""
    assessment = _answer_everything(Assessment(company), "yes")
    data = assessment.to_dict()
    assert data["overall_maturity"] == 5
    first = data["conditions"][0]
    assert "maturity" in first
    assert "weight" in first


def test_cli_report_shows_maturity(gavaza_home, tmp_path, capsys) -> None:
    """The report must render maturity levels."""
    assert main(["init", "--name", "Acme (Pty) Ltd"]) == 0
    capsys.readouterr()
    answers = {item_id: "yes" for item_id in ALL_ITEM_IDS}
    answers_file = tmp_path / "answers.json"
    answers_file.write_text(str(answers).replace("'", '"'), encoding="utf-8")
    assert main(["assess", "--answers", str(answers_file)]) == 0
    capsys.readouterr()
    assert main(["report"]) == 0
    out = capsys.readouterr().out
    assert "Maturity" in out
    assert "Optimising" in out
