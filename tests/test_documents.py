"""Tests for the expanded compliance document suite."""

from __future__ import annotations

from gavaza.cli import main
from gavaza.config import Company
from gavaza.documents import (
    generate_consent_template,
    generate_dsr_form,
    generate_operator_agreement,
    generate_pia_questionnaire,
    generate_retention_schedule,
)
from gavaza.generate import DOC_FILENAMES, generate_document, write_docs


def _company() -> Company:
    """A company for document generation tests."""
    return Company(
        name="Acme (Pty) Ltd",
        reg_no="2026/000000/07",
        email="privacy@acme.co.za",
        info_officer="A. Officer",
    )


def test_operator_agreement_obligations() -> None:
    """The operator agreement must carry the section 21 obligations."""
    import re

    text = re.sub(r"\s+", " ", generate_operator_agreement(_company())).lower()
    for term in ("documented instructions", "confidentiality", "sub-operator", "return or securely destroy"):
        assert term.lower() in text


def test_dsr_form_contains_rights() -> None:
    """The DSR form must cover access, correction, and objection."""
    text = generate_dsr_form(_company())
    assert "Access" in text
    assert "Correction" in text
    assert "Objection" in text
    assert "30 days" in text


def test_consent_template_contains_withdrawal() -> None:
    """The consent template must explain withdrawal of consent."""
    text = generate_consent_template(_company())
    assert "withdraw it at any time" in text
    assert "explicit" in text


def test_retention_schedule_has_rows() -> None:
    """The retention schedule must include record categories."""
    text = generate_retention_schedule(_company())
    assert "Employee records" in text
    assert "Financial records" in text
    assert "Retention period" in text


def test_pia_questionnaire_has_questions() -> None:
    """The PIA questionnaire must cover risk areas."""
    text = generate_pia_questionnaire(_company())
    assert "lawful basis" in text
    assert "children" in text
    assert "outside South Africa" in text


def test_generate_document_new_names() -> None:
    """All eight document names must generate content."""
    company = _company()
    for doc in DOC_FILENAMES:
        content = generate_document(company, doc)
        assert content.strip()
    assert len(DOC_FILENAMES) == 8


def test_write_docs_writes_all(tmp_path) -> None:
    """write_docs must write every requested document."""
    out = tmp_path / "docs"
    written = write_docs(_company(), docs=list(DOC_FILENAMES), out_dir=out)
    assert len(written) == 8
    for doc, path in written.items():
        assert path.exists()
        assert path.name == DOC_FILENAMES[doc]


def test_cli_generate_new_docs(gavaza_home, tmp_path, capsys) -> None:
    """The CLI must generate the new document types."""
    assert main(["init", "--name", "Acme (Pty) Ltd"]) == 0
    capsys.readouterr()
    out = tmp_path / "docs"
    assert main(["generate", "--docs", "operator", "retention", "--out", str(out)]) == 0
    capsys.readouterr()
    assert (out / "operator-agreement.md").exists()
    assert (out / "retention-schedule.md").exists()
