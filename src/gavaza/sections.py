"""Additional POPIA compliance sections beyond the eight conditions.

The eight conditions in :mod:`gavaza.conditions` drive the core
assessment. This module documents further POPIA obligations that apply
alongside them:

- special personal information (sections 26-27)
- personal information of children (sections 34-35)
- cross-border transfers (section 72)
- automated decision-making (section 71)
- direct marketing (section 69)
- data subject rights (sections 23-25)

Each section carries a checklist of requirements with practical
guidance. These sections do not change the eight-condition score.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SectionItem:
    """One requirement inside an additional section."""

    id: str
    requirement: str
    guidance: str


@dataclass(frozen=True)
class Section:
    """An additional POPIA compliance area with its checklist."""

    slug: str
    name: str
    act_reference: str
    description: str
    items: tuple[SectionItem, ...] = field(default_factory=tuple)


SECTIONS: tuple[Section, ...] = (
    Section(
        slug="special_personal_information",
        name="Special Personal Information",
        act_reference="s.26-27",
        description=(
            "POPIA restricts processing of personal information concerning "
            "religious or philosophical beliefs, race or ethnic origin, trade "
            "union membership, political persuasion, health or sex life, "
            "biometric data, and criminal behaviour."
        ),
        items=(
            SectionItem(
                id="spi-1",
                requirement=(
                    "Identify every category of special personal information the "
                    "company processes."
                ),
                guidance=(
                    "Review HR, health, security, and marketing data flows for "
                    "special categories; document each one in the record of "
                    "processing activities."
                ),
            ),
            SectionItem(
                id="spi-2",
                requirement=(
                    "Establish a lawful basis for each special-category "
                    "processing activity."
                ),
                guidance=(
                    "Section 27 permits processing with explicit consent, for "
                    "legal claims, for legal obligations, to protect vital "
                    "interests, or for purposes of a religious, political, or "
                    "trade-union body's legitimate activities. Document the "
                    "basis for each activity."
                ),
            ),
            SectionItem(
                id="spi-3",
                requirement=(
                    "Apply additional safeguards to special-category data."
                ),
                guidance=(
                    "Use stronger access controls, encryption, and restricted "
                    "retention for special categories; limit access to staff "
                    "with a need to know."
                ),
            ),
            SectionItem(
                id="spi-4",
                requirement=(
                    "Obtain explicit, informed consent where consent is the "
                    "lawful basis."
                ),
                guidance=(
                    "Consent must be specific, informed, and freely given; "
                    "record when and how consent was obtained, and honour "
                    "withdrawal promptly."
                ),
            ),
        ),
    ),
    Section(
        slug="children",
        name="Personal Information of Children",
        act_reference="s.34-35",
        description=(
            "A competent person (a parent or guardian) must consent to the "
            "processing of a child's personal information, and processing of "
            "children's information is generally prohibited without such "
            "consent."
        ),
        items=(
            SectionItem(
                id="chi-1",
                requirement=(
                    "Determine whether the company processes personal "
                    "information of children."
                ),
                guidance=(
                    "Review customer, marketing, and education-facing services "
                    "for child data subjects; document the channels through "
                    "which their information is collected."
                ),
            ),
            SectionItem(
                id="chi-2",
                requirement=(
                    "Obtain the consent of a competent person for processing a "
                    "child's information."
                ),
                guidance=(
                    "Design consent flows that identify a parent or guardian "
                    "and record their consent and identity verification."
                ),
            ),
            SectionItem(
                id="chi-3",
                requirement=(
                    "Confirm that processing of a child's information serves "
                    "the child's best interests."
                ),
                guidance=(
                    "Section 35 requires the general protection of a child's "
                    "lawful interests; document the necessity and benefit of "
                    "each processing activity involving children."
                ),
            ),
        ),
    ),
    Section(
        slug="cross_border",
        name="Cross-Border Transfers",
        act_reference="s.72",
        description=(
            "Personal information may only be transferred outside South "
            "Africa to a jurisdiction with an adequate level of protection, "
            "or under safeguards that provide substantially similar "
            "protection, or with consent or another lawful ground."
        ),
        items=(
            SectionItem(
                id="cb-1",
                requirement=(
                    "Map every transfer of personal information outside South "
                    "Africa."
                ),
                guidance=(
                    "List foreign processors, cloud providers, group "
                    "companies, and contractors; note the destination country "
                    "for each transfer."
                ),
            ),
            SectionItem(
                id="cb-2",
                requirement=(
                    "Assess the adequacy of protection in each destination "
                    "country."
                ),
                guidance=(
                    "Check the Information Regulator's guidance and binding "
                    "corporate rules; document the adequacy assessment or the "
                    "safeguard relied on."
                ),
            ),
            SectionItem(
                id="cb-3",
                requirement=(
                    "Put contractual safeguards in place for cross-border "
                    "processing."
                ),
                guidance=(
                    "Use processing agreements with clauses that bind the "
                    "foreign party to protection substantially similar to "
                    "POPIA; include data-subject rights and enforcement "
                    "mechanisms."
                ),
            ),
            SectionItem(
                id="cb-4",
                requirement=(
                    "Document the lawful ground for each cross-border transfer."
                ),
                guidance=(
                    "Grounds include adequacy, binding corporate rules, "
                    "contractual protection, consent, contract performance, "
                    "and public interest; record the ground per transfer."
                ),
            ),
        ),
    ),
    Section(
        slug="automated_decisions",
        name="Automated Decision-Making",
        act_reference="s.71",
        description=(
            "A person may not be subject to a decision that produces legal "
            "consequences, based solely on automated processing, unless the "
            "decision is required by a contract, authorised by law, or made "
            "with explicit consent and protective measures."
        ),
        items=(
            SectionItem(
                id="ad-1",
                requirement=(
                    "Identify every automated decision with legal consequences "
                    "for data subjects."
                ),
                guidance=(
                    "Review credit scoring, fraud screening, hiring, and "
                    "pricing systems for decisions made solely by automated "
                    "means."
                ),
            ),
            SectionItem(
                id="ad-2",
                requirement=(
                    "Establish the lawful ground for each automated decision."
                ),
                guidance=(
                    "Grounds are contract performance, authorisation by law, "
                    "or explicit consent; document the ground for each "
                    "system."
                ),
            ),
            SectionItem(
                id="ad-3",
                requirement=(
                    "Provide protective measures for data subjects affected by "
                    "automated decisions."
                ),
                guidance=(
                    "Offer the chance to make representations, provide "
                    "meaningful explanation of the logic, and allow human "
                    "review of the outcome."
                ),
            ),
        ),
    ),
    Section(
        slug="direct_marketing",
        name="Direct Marketing",
        act_reference="s.69",
        description=(
            "Direct marketing by electronic means requires consent, except "
            "for existing customers where the customer is given the right to "
            "opt out; every marketing communication must offer an "
            "opt-out mechanism."
        ),
        items=(
            SectionItem(
                id="dm-1",
                requirement=(
                    "Obtain consent before sending electronic direct marketing "
                    "to new contacts."
                ),
                guidance=(
                    "Use opt-in consent for email, SMS, and phone marketing; "
                    "record consent with a timestamp and the channel used."
                ),
            ),
            SectionItem(
                id="dm-2",
                requirement=(
                    "Provide an opt-out in every marketing communication."
                ),
                guidance=(
                    "Include a working unsubscribe or reply-stop mechanism in "
                    "each message; honour opt-outs promptly and permanently."
                ),
            ),
            SectionItem(
                id="dm-3",
                requirement=(
                    "Manage the existing-customer exception correctly."
                ),
                guidance=(
                    "Section 69(2) allows marketing to existing customers for "
                    "similar products or services, but each message must "
                    "offer the right to object; never market to a customer "
                    "who has objected."
                ),
            ),
            SectionItem(
                id="dm-4",
                requirement=(
                    "Maintain a do-not-contact register."
                ),
                guidance=(
                    "Keep a suppression list of opted-out and objected "
                    "contacts; check it before every campaign."
                ),
            ),
        ),
    ),
    Section(
        slug="data_subject_rights",
        name="Data Subject Rights",
        act_reference="s.23-25",
        description=(
            "Data subjects may request access to their personal information, "
            "request correction or deletion of inaccurate information, and "
            "object to processing on reasonable grounds. Requests must be "
            "processed without undue delay."
        ),
        items=(
            SectionItem(
                id="dsr-1",
                requirement=(
                    "Maintain a process for access requests under section 23."
                ),
                guidance=(
                    "Publish a request channel, verify the requester's "
                    "identity, search all systems for the information, and "
                    "respond within a reasonable time; the Regulator's "
                    "guidance uses 30 days."
                ),
            ),
            SectionItem(
                id="dsr-2",
                requirement=(
                    "Correct or delete inaccurate personal information on "
                    "request."
                ),
                guidance=(
                    "Section 24 requires correction or deletion of "
                    "inaccurate, misleading, or incomplete information; "
                    "notify third parties who received the information."
                ),
            ),
            SectionItem(
                id="dsr-3",
                requirement=(
                    "Handle objections to processing under section 25."
                ),
                guidance=(
                    "Assess each objection on reasonable grounds; stop "
                    "processing unless the company can demonstrate "
                    "compelling legitimate grounds."
                ),
            ),
            SectionItem(
                id="dsr-4",
                requirement=(
                    "Record every data subject request and its outcome."
                ),
                guidance=(
                    "Keep a request register with dates, actions taken, and "
                    "responses; use it to demonstrate compliance."
                ),
            ),
        ),
    ),
)

SECTION_MAP: dict[str, Section] = {section.slug: section for section in SECTIONS}


def get_section(slug: str) -> Section:
    """Return the section with ``slug``, raising KeyError when unknown."""
    return SECTION_MAP[slug]


def section_lookup() -> dict[str, tuple[str, str, SectionItem]]:
    """Return {item_id: (slug, section name, item)} for every section item."""
    return {
        item.id: (section.slug, section.name, item)
        for section in SECTIONS
        for item in section.items
    }
