"""Tests for the additional POPIA compliance sections.

The eight conditions model the core assessment. These sections cover
additional POPIA obligations: special personal information, children,
cross-border transfers, automated decisions, direct marketing, and data
subject rights.
"""

from __future__ import annotations

import pytest

from gavaza.cli import main
from gavaza.sections import (
    SECTION_MAP,
    SECTIONS,
    get_section,
    section_lookup,
)

EXPECTED_SLUGS = {
    "special_personal_information",
    "children",
    "cross_border",
    "automated_decisions",
    "direct_marketing",
    "data_subject_rights",
}


def test_six_sections_exist() -> None:
    """The additional sections must cover six POPIA areas."""
    assert len(SECTIONS) == 6
    assert {section.slug for section in SECTIONS} == EXPECTED_SLUGS


def test_section_ids_unique() -> None:
    """Item ids must be unique across every section."""
    ids = [item.id for section in SECTIONS for item in section.items]
    assert len(ids) == len(set(ids))


def test_sections_have_act_references() -> None:
    """Every section must reference its POPIA sections."""
    for section in SECTIONS:
        assert section.act_reference.startswith("s.")
        assert len(section.items) >= 3


def test_sections_have_guidance() -> None:
    """Every item must carry a requirement and guidance text."""
    for section in SECTIONS:
        for item in section.items:
            assert item.requirement.strip()
            assert item.guidance.strip()


def test_special_personal_information_content() -> None:
    """The special information section must name protected categories."""
    section = get_section("special_personal_information")
    text = " ".join(item.requirement for item in section.items).lower()
    assert "biometric" in text
    assert "health" in text


def test_cross_border_mentions_adequacy() -> None:
    """The cross-border section must cover transfer safeguards."""
    section = get_section("cross_border")
    text = " ".join(item.requirement for item in section.items).lower()
    assert "adequacy" in text or "consent" in text


def test_data_subject_rights_covers_access() -> None:
    """The rights section must cover access, correction and objection."""
    section = get_section("data_subject_rights")
    text = " ".join(item.requirement for item in section.items).lower()
    assert "access" in text
    assert "correction" in text
    assert "object" in text


def test_get_section_raises_for_unknown_slug() -> None:
    """An unknown slug must raise KeyError."""
    with pytest.raises(KeyError):
        get_section("nope")


def test_section_map_and_lookup_consistent() -> None:
    """SECTION_MAP and section_lookup must agree with SECTIONS."""
    assert set(SECTION_MAP) == EXPECTED_SLUGS
    lookup = section_lookup()
    total_items = sum(len(section.items) for section in SECTIONS)
    assert len(lookup) == total_items
    for item_id, (slug, _name, item) in lookup.items():
        assert item.id == item_id
        assert slug in EXPECTED_SLUGS


def test_cli_sections_command(capsys) -> None:
    """``gavaza sections`` must list all sections and items."""
    assert main(["sections"]) == 0
    out = capsys.readouterr().out
    assert "special_personal_information" in out
    assert "Cross-Border Transfers" in out
    assert "s.72" in out


def test_cli_sections_slug_filter(capsys) -> None:
    """``gavaza sections --slug X`` must print only that section."""
    assert main(["sections", "--slug", "direct_marketing"]) == 0
    out = capsys.readouterr().out
    assert "Direct Marketing" in out
    assert "Cross-Border" not in out
