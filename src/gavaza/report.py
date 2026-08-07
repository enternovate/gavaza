"""Assessment reports: markdown, HTML and JSON.

A report summarises the assessment with per-condition scores, the overall
score and grade, and a prioritised remediation list (worst-scoring
conditions first).
"""

from __future__ import annotations

import html
import json
from datetime import UTC, datetime
from pathlib import Path

from gavaza.assess import Assessment, maturity_label
from gavaza.conditions import CONDITION_MAP


def _condition_rows(assessment: Assessment) -> list[tuple[str, str, float, str]]:
    """Return (name, slug, score, status) for each of the eight conditions."""
    rows = []
    for slug, condition in CONDITION_MAP.items():
        score = assessment.condition_score(slug)
        status = "Compliant" if score >= 80 else ("Partial" if score >= 50 else "At risk")
        rows.append((condition.name, slug, score, status))
    return rows


def _remediation_section(assessment: Assessment) -> str:
    """Markdown list of prioritised remediation actions."""
    items = assessment.remediation_items()
    if not items:
        return "_No remediation items — every checklist item is answered yes._"
    lines = [
        (
            "Prioritised by condition score (worst first). Address items answered "
            "**no** before **partial** within each condition."
        ),
        "",
    ]
    for item in items:
        severity = "Critical" if item["answer"] == "no" else "Improvement"
        lines.append(
            f"- **[{severity}] {item['condition']}** ({item['condition_score']:.0f}/100) — "
            f"{item['question']}\n"
            f"  - Current answer: {item['answer']}"
            + (f" — note: {item['note']}" if item["note"] else "")
            + f"\n  - Remediation: {item['remediation']}"
        )
    return "\n".join(lines)


def render_markdown(assessment: Assessment) -> str:
    """Render the assessment as a markdown report."""
    score = assessment.overall_score()
    lines = [
        "# POPIA Compliance Assessment Report",
        "",
        f"- **Company:** {assessment.company.name}",
        f"- **Date:** {datetime.now(UTC).date().isoformat()}",
        f"- **Overall score:** {score:.1f}/100",
        f"- **Grade:** {assessment.grade()}",
        f"- **Maturity:** {maturity_label(assessment.overall_maturity())} "
        f"(level {assessment.overall_maturity()} of 5)",
        "",
        "## Condition scores",
        "",
        "| Condition | Score | Maturity | Status |",
        "|---|---|---|---|",
    ]
    for name, slug, condition_score, status in _condition_rows(assessment):
        lines.append(
            f"| {name} (`{slug}`) | {condition_score:.1f}/100 | "
            f"{assessment.condition_maturity(slug)} | {status} |"
        )
    lines += ["", "## Prioritised remediation", "", _remediation_section(assessment), ""]
    return "\n".join(lines)


def render_html(assessment: Assessment) -> str:
    """Render the assessment as a self-contained HTML report."""
    score = assessment.overall_score()
    rows = "".join(
        "<tr>"
        f"<td>{html.escape(name)}</td>"
        f"<td>{condition_score:.1f}/100</td>"
        f"<td>{html.escape(status)}</td>"
        "</tr>"
        for name, _slug, condition_score, status in _condition_rows(assessment)
    )
    remediation_items = assessment.remediation_items()
    if remediation_items:
        remediation = "<ul>" + "".join(
            "<li>"
            f"<strong>[{'Critical' if item['answer'] == 'no' else 'Improvement'}] "
            f"{html.escape(item['condition'])}</strong> "
            f"({item['condition_score']:.0f}/100) — {html.escape(item['question'])}<br>"
            f"<em>Remediation:</em> {html.escape(item['remediation'])}"
            + (f"<br><em>Note:</em> {html.escape(item['note'])}" if item["note"] else "")
            + "</li>"
            for item in remediation_items
        ) + "</ul>"
    else:
        remediation = "<p>No remediation items — every checklist item is answered yes.</p>"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>POPIA Compliance Assessment Report — {html.escape(assessment.company.name)}</title>
<style>
body {{ font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; margin: 2rem auto; max-width: 56rem; color: #1a1a2e; line-height: 1.5; }}
h1 {{ color: #14532d; }}
table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
th, td {{ border: 1px solid #ccc; padding: 0.5rem 0.75rem; text-align: left; }}
th {{ background: #f0fdf4; }}
.score {{ font-size: 1.4rem; font-weight: bold; color: #14532d; }}
</style>
</head>
<body>
<h1>POPIA Compliance Assessment Report</h1>
<p><strong>Company:</strong> {html.escape(assessment.company.name)}<br>
<strong>Date:</strong> {datetime.now(UTC).date().isoformat()}<br>
<span class="score">Overall score: {score:.1f}/100 &mdash; Grade {assessment.grade()}</span></p>
<h2>Condition scores</h2>
<table>
<tr><th>Condition</th><th>Score</th><th>Status</th></tr>
{rows}
</table>
<h2>Prioritised remediation</h2>
{remediation}
<p><em>Generated with Gavaza {assessment.to_dict().get('version', '')}. This report is a tool, not legal advice.</em></p>
</body>
</html>
"""


def render_json(assessment: Assessment) -> str:
    """Render the assessment as a JSON document."""
    return json.dumps(assessment.to_dict(), indent=2, ensure_ascii=False)


def render(assessment: Assessment, fmt: str) -> str:
    """Render the assessment in ``json``, ``md`` or ``html`` format."""
    if fmt == "json":
        return render_json(assessment)
    if fmt == "md":
        return render_markdown(assessment)
    if fmt == "html":
        return render_html(assessment)
    raise ValueError(f"unknown report format {fmt!r}; expected json, md or html")


def summary_lines(assessment: Assessment) -> list[str]:
    """Short console summary of the assessment results."""
    score = assessment.overall_score()
    return [
        f"Assessment complete for {assessment.company.name}",
        f"Overall score: {score:.1f}/100 — grade {assessment.grade()}",
        "",
        "Per-condition scores:",
    ] + [
        f"  {name}: {condition_score:.1f}/100"
        for name, _slug, condition_score, _status in _condition_rows(assessment)
    ] + [
        "",
        f"Remediation items: {len(assessment.remediation_items())} (see report)",
    ]


def latest_results_path(home: Path | None = None) -> Path:
    """Path of the most recent assessment results file in the data dir."""
    from gavaza.config import data_dir

    base = home or data_dir()
    return base / "assessment.json"
