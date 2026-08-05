"""Tests for the eight POPIA conditions model."""

from __future__ import annotations

import pytest

from gavaza.conditions import (
    ALL_ITEM_IDS,
    CONDITION_MAP,
    CONDITIONS,
    get_condition,
    item_lookup,
)

EXPECTED_NAMES = {
    "Accountability",
    "Processing Limitation",
    "Purpose Specification",
    "Further Processing Limitation",
    "Information Quality",
    "Openness",
    "Security Safeguards",
    "Data Subject Participation",
}


def test_exactly_eight_conditions() -> None:
    """POPIA defines eight conditions for lawful processing."""
    assert len(CONDITIONS) == 8


def test_condition_names_match_popia() -> None:
    """The eight conditions carry the standard POPIA names."""
    assert {c.name for c in CONDITIONS} == EXPECTED_NAMES


def test_checklist_sizes_and_unique_ids() -> None:
    """Each condition has 4-6 checklist items and every item id is unique."""
    all_ids: list[str] = []
    for condition in CONDITIONS:
        assert 4 <= len(condition.checklist) <= 6, condition.slug
        assert condition.slug.isidentifier()
        assert condition.act_reference
        assert condition.description
        for item in condition.checklist:
            assert item.question
            assert item.remediation
            all_ids.append(item.id)
    assert len(all_ids) == len(set(all_ids))


def test_condition_map_and_lookup_consistent() -> None:
    """CONDITION_MAP and item_lookup agree with CONDITIONS."""
    assert set(CONDITION_MAP) == {c.slug for c in CONDITIONS}
    lookup = item_lookup()
    assert len(lookup) == len(ALL_ITEM_IDS) == len(set(ALL_ITEM_IDS))
    for item_id in ALL_ITEM_IDS:
        slug, name, item = lookup[item_id]
        assert item.id == item_id
        assert name == CONDITION_MAP[slug].name


def test_get_condition_raises_for_unknown_slug() -> None:
    """Unknown slugs raise KeyError rather than silently passing."""
    with pytest.raises(KeyError):
        get_condition("not_a_condition")
