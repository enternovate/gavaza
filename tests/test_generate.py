"""Tests for the document generators and the breach register CSV."""

from __future__ import annotations

from gavaza.breach import (
    BREACH_HEADER,
    BreachRecord,
    add_breach,
    ensure_register,
    list_breaches,
)
from gavaza.generate import (
    generate_paia,
    generate_privacy_policy,
    generate_processing_register,
    write_docs,
)


def test_paia_contains_company_and_sections(company) -> None:
    text = generate_paia(company)
    assert company.name in text
    assert company.reg_no in text
    assert "records the company holds" in text.lower()
    for heading in (
        "Purpose of this manual",
        "Company details",
        "Information Officer",
        "Request procedure",
        "Fees",
        "Grounds for refusal",
        "Contact",
    ):
        assert heading.lower() in text.lower(), heading


def test_privacy_policy_sections(company) -> None:
    text = generate_privacy_policy(company)
    assert company.name in text
    assert company.reg_no in text
    assert "Your rights" in text
    for heading in (
        "Who we are",
        "What we collect",
        "Why we collect it",
        "Sharing",
        "Security",
        "Retention",
        "Your rights",
        "Contact",
    ):
        assert f"## {heading}" in text, heading


def test_register_has_rows(company) -> None:
    text = generate_processing_register(company)
    assert company.name in text
    lines = text.splitlines()
    header = [line for line in lines if line.startswith("| Activity |")]
    assert header, "expected the register table header"
    for column in (
        "Activity",
        "Purpose",
        "Data subjects",
        "Categories of personal information",
        "Retention",
        "Lawful basis",
        "Sharing",
    ):
        assert column in header[0], column
    data_rows = [
        line
        for line in lines
        if line.startswith("| ") and not line.startswith("|---") and "|" in line[2:]
    ]
    assert len(data_rows) >= 3, "expected several processing activity rows"


def test_register_accepts_custom_activities(company) -> None:
    activities = [
        {
            "activity": "Research surveys",
            "purpose": "Market research",
            "data_subjects": "Customers",
            "categories": "Emails",
            "retention": "1 year",
            "lawful_basis": "Consent",
            "sharing": "None",
        }
    ]
    text = generate_processing_register(company, activities=activities)
    assert "Research surveys" in text
    assert "Market research" in text


def test_breach_csv_header_and_roundtrip(company, tmp_path) -> None:
    path = tmp_path / "breach-register.csv"
    ensure_register(path)
    with path.open("r", encoding="utf-8") as handle:
        assert handle.readline().strip().split(",") == BREACH_HEADER
    add_breach(
        BreachRecord(
            description="phishing campaign",
            categories="names, email addresses",
            affected_count=42,
            risk_assessment="medium — possible credential exposure",
            notification_status="regulator notified",
        ),
        path=path,
    )
    records = list_breaches(path)
    assert len(records) == 1
    assert records[0].description == "phishing campaign"
    assert records[0].affected_count == "42"
    assert records[0].notification_status == "regulator notified"


def test_write_docs_writes_files(company, tmp_path) -> None:
    out = tmp_path / "out"
    written = write_docs(company, docs=("paia", "privacy", "register"), out_dir=out)
    assert set(written) == {"paia", "privacy", "register"}
    for path in written.values():
        assert path.exists()
        assert path.stat().st_size > 0
