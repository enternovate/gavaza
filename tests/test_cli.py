"""End-to-end tests for the Gavaza command-line interface."""

from __future__ import annotations

import json

import pytest

from gavaza import __version__
from gavaza.cli import main
from gavaza.conditions import ALL_ITEM_IDS

EXPECTED_CONDITION_NAMES = (
    "Accountability",
    "Processing Limitation",
    "Purpose Specification",
    "Further Processing Limitation",
    "Information Quality",
    "Openness",
    "Security Safeguards",
    "Data Subject Participation",
)

ALL_YES = {item_id: "yes" for item_id in ALL_ITEM_IDS}


def _write_answers(tmp_path, answers) -> str:
    path = tmp_path / "answers.json"
    path.write_text(json.dumps(answers), encoding="utf-8")
    return str(path)


def test_version_flag(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_conditions_command(capsys) -> None:
    assert main(["conditions"]) == 0
    out = capsys.readouterr().out
    for name in EXPECTED_CONDITION_NAMES:
        assert name in out


def test_init_with_flags(gavaza_home, capsys) -> None:
    rc = main(
        [
            "init",
            "--name",
            "Acme (Pty) Ltd",
            "--reg",
            "2026/123456/07",
            "--email",
            "info@acme.co.za",
            "--info-officer",
            "Jane Dlamini",
        ]
    )
    assert rc == 0
    cfg = gavaza_home / "company.json"
    assert cfg.exists()
    data = json.loads(cfg.read_text(encoding="utf-8"))
    assert data["name"] == "Acme (Pty) Ltd"
    assert data["info_officer"] == "Jane Dlamini"
    assert "configuration written" in capsys.readouterr().out


def test_init_from_company_json(tmp_path, gavaza_home) -> None:
    source = tmp_path / "company.json"
    source.write_text(json.dumps({"name": "Widget Co", "reg_no": "W-1"}), encoding="utf-8")
    assert main(["init", str(source)]) == 0
    data = json.loads((gavaza_home / "company.json").read_text(encoding="utf-8"))
    assert data["name"] == "Widget Co"
    assert data["reg_no"] == "W-1"


def test_init_without_name_fails(gavaza_home, capsys) -> None:
    assert main(["init"]) == 2
    assert "error" in capsys.readouterr().err


def test_assess_requires_config(gavaza_home, capsys) -> None:
    assert main(["assess"]) == 1
    assert "gavaza init" in capsys.readouterr().err


def test_e2e_init_assess_generate(gavaza_home, tmp_path, capsys) -> None:
    """init -> assess with scripted answers -> generate -> files exist."""
    assert (
        main(
            [
                "init",
                "--name",
                "Full Stack (Pty) Ltd",
                "--reg",
                "2026/99",
                "--email",
                "office@fullstack.co.za",
                "--info-officer",
                "Sipho Mokoena",
            ]
        )
        == 0
    )
    answers = _write_answers(tmp_path, ALL_YES)
    assert main(["assess", "--answers", answers]) == 0
    results = gavaza_home / "assessment.json"
    assert results.exists()
    data = json.loads(results.read_text(encoding="utf-8"))
    assert data["overall_score"] == 100.0
    assert data["grade"] == "A"
    assert data["company"] == "Full Stack (Pty) Ltd"
    out = tmp_path / "docs"
    assert main(["generate", "--docs", "all", "--out", str(out)]) == 0
    for fname in (
        "PAIA-manual.md",
        "privacy-policy.md",
        "record-of-processing-activities.md",
    ):
        assert (out / fname).exists(), fname


def test_assess_baseline_and_report_formats(gavaza_home, tmp_path, capsys) -> None:
    """A default (unanswered) assessment and each report format render."""
    assert main(["init", "--name", "Report Co", "--email", "r@c.co.za"]) == 0
    assert main(["assess"]) == 0  # baseline: everything unanswered
    assert main(["report", "--format", "json", "--out", str(tmp_path / "r.json")]) == 0
    assert main(["report", "--format", "md", "--out", str(tmp_path / "r.md")]) == 0
    assert main(["report", "--format", "html", "--out", str(tmp_path / "r.html")]) == 0
    jdata = json.loads((tmp_path / "r.json").read_text(encoding="utf-8"))
    assert jdata["overall_score"] == 0.0
    assert jdata["grade"] == "F"
    md = (tmp_path / "r.md").read_text(encoding="utf-8")
    assert "Condition scores" in md
    assert "Prioritised remediation" in md
    assert "Report Co" in md
    html = (tmp_path / "r.html").read_text(encoding="utf-8")
    assert "<html" in html
    assert "Accountability" in html
    # Default format goes to stdout with no --out.
    assert main(["report", "--format", "md"]) == 0
    assert "Overall score" in capsys.readouterr().out


def test_report_prioritises_remediation(gavaza_home, tmp_path) -> None:
    assert main(["init", "--name", "Fix Me Co"]) == 0
    answers = {
        item_id: ("no" if item_id.startswith("ss-") else "yes") for item_id in ALL_ITEM_IDS
    }
    assert main(["assess", "--answers", _write_answers(tmp_path, answers)]) == 0
    assert main(["report", "--format", "md", "--out", str(tmp_path / "r.md")]) == 0
    md = (tmp_path / "r.md").read_text(encoding="utf-8")
    assert "Security Safeguards" in md
    assert "Critical" in md


def test_breach_add_prints_checklist_and_lists(gavaza_home, capsys) -> None:
    rc = main(
        [
            "breach",
            "add",
            "--description",
            "unauthorised access to CRM",
            "--categories",
            "customer names and emails",
            "--affected",
            "120",
            "--risk",
            "high — financial data involved",
            "--status",
            "regulator notified",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "72-hour notification checklist" in out
    assert "72 hours" in out
    register = gavaza_home / "breach-register.csv"
    assert register.exists()
    lines = register.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert lines[0].split(",") == [
        "date",
        "description",
        "categories",
        "affected_count",
        "risk_assessment",
        "notification_status",
    ]
    assert "120" in lines[1]
    assert "unauthorised access to CRM" in lines[1]
    assert main(["breach", "list"]) == 0
    assert "unauthorised access to CRM" in capsys.readouterr().out


def test_breach_timeline_and_bad_affected(gavaza_home, capsys) -> None:
    assert main(["breach", "timeline"]) == 0
    assert "72 hours" in capsys.readouterr().out
    with pytest.raises(SystemExit):
        main(
            [
                "breach",
                "add",
                "--description",
                "oops",
                "--affected",
                "not-a-number",
            ]
        )
