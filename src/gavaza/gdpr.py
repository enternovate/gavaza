"""Mapping between POPIA obligations and the GDPR.

Each POPIA condition and additional section maps to the closest GDPR
provision, with a note on the differences. The map is a reference aid;
it is not legal advice and it does not replace a full cross-border
compliance analysis.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class GdprMapping:
    """One POPIA to GDPR mapping row."""

    popia_reference: str
    popia_area: str
    gdpr_articles: str
    difference_note: str

    def to_dict(self) -> dict[str, str]:
        """Return the row as a plain dict."""
        return asdict(self)


MAPPINGS: tuple[GdprMapping, ...] = (
    GdprMapping(
        popia_reference="s.8",
        popia_area="Accountability",
        gdpr_articles="Art. 5(2), Art. 24",
        difference_note=(
            "Both laws require a responsible party to demonstrate compliance; "
            "the GDPR adds data protection by design and by default (Art. 25) "
            "and the data protection officer role (Art. 37)."
        ),
    ),
    GdprMapping(
        popia_reference="s.9-11",
        popia_area="Processing Limitation",
        gdpr_articles="Art. 5(1)(a), (c); Art. 6",
        difference_note=(
            "Both require lawfulness and data minimisation. The GDPR's list "
            "of lawful bases (Art. 6) is wider than POPIA's, which centres "
            "on consent and justifiable grounds."
        ),
    ),
    GdprMapping(
        popia_reference="s.13",
        popia_area="Purpose Specification",
        gdpr_articles="Art. 5(1)(b)",
        difference_note=(
            "Both require collection for specific, explicit, and legitimate "
            "purposes. POPIA adds the section 13 notice obligations at "
            "collection."
        ),
    ),
    GdprMapping(
        popia_reference="s.14",
        popia_area="Further Processing Limitation",
        gdpr_articles="Art. 6(4)",
        difference_note=(
            "The GDPR permits further processing for a compatible purpose; "
            "POPIA requires the further purpose to be compatible with the "
            "original purpose, with consent or legal grounds."
        ),
    ),
    GdprMapping(
        popia_reference="s.16",
        popia_area="Information Quality",
        gdpr_articles="Art. 5(1)(d)",
        difference_note=(
            "Both require accuracy and reasonable steps to keep records "
            "complete and up to date."
        ),
    ),
    GdprMapping(
        popia_reference="s.17-18",
        popia_area="Openness",
        gdpr_articles="Art. 12-14",
        difference_note=(
            "Both require transparency. The GDPR mandates detailed privacy "
            "notices; POPIA requires the section 18 notice at collection."
        ),
    ),
    GdprMapping(
        popia_reference="s.19-22",
        popia_area="Security Safeguards",
        gdpr_articles="Art. 5(1)(f), Art. 32-34",
        difference_note=(
            "Both require appropriate security measures and breach "
            "notification. The GDPR notifies the supervisory authority "
            "within 72 hours; POPIA requires notification to the Regulator "
            "and data subjects as soon as reasonably possible."
        ),
    ),
    GdprMapping(
        popia_reference="s.23-25",
        popia_area="Data Subject Participation",
        gdpr_articles="Art. 15-22",
        difference_note=(
            "Both grant access, correction, and objection rights. The GDPR "
            "adds erasure (Art. 17) and data portability (Art. 20)."
        ),
    ),
    GdprMapping(
        popia_reference="s.26-27",
        popia_area="Special Personal Information",
        gdpr_articles="Art. 9",
        difference_note=(
            "Both restrict special categories; the GDPR lists the same core "
            "categories plus trade union membership and adds processing for "
            "substantial public interest."
        ),
    ),
    GdprMapping(
        popia_reference="s.34-35",
        popia_area="Personal Information of Children",
        gdpr_articles="Art. 8",
        difference_note=(
            "The GDPR sets 16 as the age of consent for information society "
            "services (member states may lower it to 13); POPIA requires "
            "consent of a competent person without a fixed age in the Act."
        ),
    ),
    GdprMapping(
        popia_reference="s.72",
        popia_area="Cross-Border Transfers",
        gdpr_articles="Art. 44-49",
        difference_note=(
            "Both restrict transfers to jurisdictions with adequate "
            "protection. The GDPR provides adequacy decisions, standard "
            "contractual clauses, and binding corporate rules as transfer "
            "tools."
        ),
    ),
    GdprMapping(
        popia_reference="s.71",
        popia_area="Automated Decision-Making",
        gdpr_articles="Art. 22",
        difference_note=(
            "Both restrict solely automated decisions with legal effects; "
            "the GDPR requires meaningful explanation and human review "
            "rights."
        ),
    ),
    GdprMapping(
        popia_reference="s.69",
        popia_area="Direct Marketing",
        gdpr_articles="Art. 21(2)-(3)",
        difference_note=(
            "Both give data subjects the right to object to direct "
            "marketing; POPIA requires consent for electronic marketing "
            "with a limited existing-customer exception."
        ),
    ),
)


def mapping_table() -> list[dict[str, str]]:
    """Return every mapping row as a dict."""
    return [mapping.to_dict() for mapping in MAPPINGS]


def lookup(popia_reference: str) -> GdprMapping | None:
    """Return the mapping for a POPIA reference, or None."""
    for mapping in MAPPINGS:
        if mapping.popia_reference == popia_reference:
            return mapping
    return None


def render_markdown() -> str:
    """Render the mapping as a markdown table."""
    lines = [
        "# POPIA to GDPR Mapping",
        "",
        "| POPIA | Area | GDPR | Difference note |",
        "|---|---|---|---|",
    ]
    for mapping in MAPPINGS:
        lines.append(
            f"| {mapping.popia_reference} | {mapping.popia_area} | "
            f"{mapping.gdpr_articles} | {mapping.difference_note} |"
        )
    lines.append("")
    lines.append(
        "_This map is a reference aid, not legal advice. Review it with a "
        "qualified professional before relying on it._"
    )
    return "\n".join(lines)


def render_json() -> str:
    """Render the mapping as a JSON document."""
    return json.dumps(mapping_table(), indent=2, ensure_ascii=False)
