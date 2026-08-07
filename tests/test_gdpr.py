"""Tests for the POPIA to GDPR mapping."""

from __future__ import annotations

from gavaza.cli import main
from gavaza.gdpr import (
    MAPPINGS,
    lookup,
    mapping_table,
    render_json,
    render_markdown,
)


def test_mappings_cover_eight_conditions() -> None:
    """Every POPIA condition must have a GDPR mapping."""
    references = {mapping.popia_reference for mapping in MAPPINGS}
    for expected in ("s.8", "s.9-11", "s.13", "s.14", "s.16", "s.17-18", "s.19-22", "s.23-25"):
        assert expected in references


def test_mappings_cover_additional_sections() -> None:
    """The special sections must map to GDPR articles too."""
    references = {mapping.popia_reference for mapping in MAPPINGS}
    for expected in ("s.26-27", "s.34-35", "s.72", "s.71", "s.69"):
        assert expected in references


def test_all_mappings_have_articles() -> None:
    """Every row must cite at least one GDPR article."""
    for mapping in MAPPINGS:
        assert mapping.gdpr_articles.startswith("Art.")
        assert mapping.difference_note.strip()


def test_lookup_finds_mapping() -> None:
    """Lookup must find a mapping by POPIA reference."""
    mapping = lookup("s.72")
    assert mapping is not None
    assert mapping.popia_area == "Cross-Border Transfers"
    assert lookup("s.999") is None


def test_mapping_table_shape() -> None:
    """The table must serialize every row as a dict."""
    rows = mapping_table()
    assert len(rows) == len(MAPPINGS)
    for row in rows:
        assert set(row) == {"popia_reference", "popia_area", "gdpr_articles", "difference_note"}


def test_render_markdown_has_headers() -> None:
    """The markdown render must include the table header."""
    text = render_markdown()
    assert "| POPIA | Area | GDPR | Difference note |" in text
    assert "Cross-Border Transfers" in text


def test_render_json_parses() -> None:
    """The JSON render must parse as a list of rows."""
    import json

    rows = json.loads(render_json())
    assert len(rows) == len(MAPPINGS)


def test_cli_gdpr_map(capsys) -> None:
    """``gavaza gdpr-map`` must print the mapping table."""
    assert main(["gdpr-map"]) == 0
    out = capsys.readouterr().out
    assert "POPIA to GDPR Mapping" in out
    assert "s.72" in out


def test_cli_gdpr_map_json(capsys) -> None:
    """``gavaza gdpr-map --format json`` must print JSON."""
    import json

    assert main(["gdpr-map", "--format", "json"]) == 0
    rows = json.loads(capsys.readouterr().out)
    assert len(rows) == len(MAPPINGS)
