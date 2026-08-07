"""Tests for the CSV report export."""

from __future__ import annotations

import csv
import io

from gavaza.cli import main
from gavaza.report import render_csv


def test_render_csv_has_headers_and_rows(gavaza_home, tmp_path) -> None:
    """The CSV report must carry overall and per-condition rows."""
    assert main(["init", "--name", "Csv Co"]) == 0
    results = tmp_path / "assessment.json"
    assert main(["assess", "--out", str(results)]) == 0
    content = render_csv(_load(results))
    rows = list(csv.reader(io.StringIO(content)))
    assert rows[0] == ["company", "date", "overall_score", "grade", "maturity"]
    assert rows[1][0] == "Csv Co"
    header_index = rows.index(["condition_slug", "condition", "score", "maturity", "status"])
    slugs = [row[0] for row in rows[header_index + 1 :]]
    assert "accountability" in slugs
    assert "security_safeguards" in slugs


def _load(path):
    """Load an assessment results JSON file."""
    import json

    from gavaza.assess import Assessment

    with open(path, encoding="utf-8") as fh:
        return Assessment.from_dict(json.load(fh), company=None)


def test_cli_report_csv_out(gavaza_home, tmp_path) -> None:
    """``gavaza report --format csv --out F`` must write a CSV file."""
    assert main(["init", "--name", "Csv Co"]) == 0
    assert main(["assess"]) == 0
    out = tmp_path / "report.csv"
    assert main(["report", "--format", "csv", "--out", str(out)]) == 0
    rows = list(csv.reader(io.StringIO(out.read_text(encoding="utf-8"))))
    assert rows[0][0] == "company"
    assert any(row and row[0] == "accountability" for row in rows)


def test_cli_report_csv_stdout(gavaza_home, capsys) -> None:
    """``gavaza report --format csv`` must print CSV to stdout."""
    assert main(["init", "--name", "Csv Co"]) == 0
    assert main(["assess"]) == 0
    capsys.readouterr()
    assert main(["report", "--format", "csv"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("company,date,overall_score,grade,maturity")
    assert "accountability," in out
