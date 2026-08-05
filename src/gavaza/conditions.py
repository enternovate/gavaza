"""The eight POPIA conditions for the lawful processing of personal information.

Each condition is modelled with a stable slug, a plain-language description
and a checklist of 4-6 questions (each with a remediation hint) that drive
the compliance assessment engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ChecklistItem:
    """A single assessment question derived from a condition's checklist."""

    id: str
    question: str
    remediation: str


@dataclass(frozen=True)
class Condition:
    """One of the eight POPIA conditions."""

    slug: str
    name: str
    act_reference: str
    description: str
    checklist: tuple[ChecklistItem, ...] = field(default_factory=tuple)

    @property
    def checklist_ids(self) -> tuple[str, ...]:
        """Return the ids of every checklist item in this condition."""
        return tuple(item.id for item in self.checklist)


CONDITIONS: tuple[Condition, ...] = (
    Condition(
        slug="accountability",
        name="Accountability",
        act_reference="s.8",
        description=(
            "The responsible party must ensure that the conditions for the lawful "
            "processing of personal information are complied with, and must be able "
            "to demonstrate that compliance to the Information Regulator."
        ),
        checklist=(
            ChecklistItem(
                id="acc-1",
                question="Has a person been appointed and documented as the Information Officer?",
                remediation=(
                    "Appoint an Information Officer (and deputies where required), "
                    "register them with the Information Regulator and publish their "
                    "contact details."
                ),
            ),
            ChecklistItem(
                id="acc-2",
                question="Is there a documented compliance programme that assigns POPIA responsibilities?",
                remediation=(
                    "Draft a compliance programme naming the Information Officer, "
                    "deputies and their duties, and keep it current."
                ),
            ),
            ChecklistItem(
                id="acc-3",
                question="Are compliance measures (policies, procedures, training) demonstrable to the Regulator?",
                remediation=(
                    "Keep evidence of policies, training registers and audits so that "
                    "compliance can be demonstrated on request."
                ),
            ),
            ChecklistItem(
                id="acc-4",
                question="Are processing activities reviewed and documented on an ongoing basis?",
                remediation="Maintain and regularly update the record of processing activities.",
            ),
            ChecklistItem(
                id="acc-5",
                question="Is there a privacy impact assessment process for high-risk processing?",
                remediation=(
                    "Adopt an assessment process for processing that may pose a high "
                    "risk to the rights of data subjects."
                ),
            ),
        ),
    ),
    Condition(
        slug="processing_limitation",
        name="Processing Limitation",
        act_reference="s.9-11",
        description=(
            "Personal information may only be processed lawfully and in a reasonable "
            "manner that does not intrude on the privacy of the data subject. "
            "Processing must be minimal, and must be justified by consent or another "
            "lawful basis."
        ),
        checklist=(
            ChecklistItem(
                id="pl-1",
                question="Is every processing activity justified by a lawful basis (consent, contract, legal obligation, legitimate interest)?",
                remediation="Document the lawful basis for each processing activity.",
            ),
            ChecklistItem(
                id="pl-2",
                question="Is only the minimum personal information necessary collected and processed?",
                remediation="Apply data minimisation when designing forms, screens and processes.",
            ),
            ChecklistItem(
                id="pl-3",
                question="Where consent is the basis, is it freely given, specific and informed?",
                remediation=(
                    "Use clear, plain-language consent requests with a genuine choice "
                    "and an easy way to withdraw."
                ),
            ),
            ChecklistItem(
                id="pl-4",
                question="Are safeguards in place against excessive or intrusive processing?",
                remediation="Review collection points for unnecessary fields and remove them.",
            ),
            ChecklistItem(
                id="pl-5",
                question="Is personal information de-identified where the purpose allows?",
                remediation="De-identify or anonymise data used for testing, analytics and research.",
            ),
            ChecklistItem(
                id="pl-6",
                question="Are third-party processors bound by written contracts to process only on instructions?",
                remediation="Sign processing agreements with every service provider that handles personal information.",
            ),
        ),
    ),
    Condition(
        slug="purpose_specification",
        name="Purpose Specification",
        act_reference="s.13",
        description=(
            "Personal information must be collected for a specific, explicitly defined "
            "and lawful purpose related to a function or activity of the responsible "
            "party, and data subjects must be told what that purpose is."
        ),
        checklist=(
            ChecklistItem(
                id="ps-1",
                question="Is a specific, defined and lawful purpose documented for each collection of personal information?",
                remediation="Write a purpose statement for each processing activity.",
            ),
            ChecklistItem(
                id="ps-2",
                question="Are data subjects informed of the purpose at the time of collection?",
                remediation="Add purpose statements to forms, notices and consent requests.",
            ),
            ChecklistItem(
                id="ps-3",
                question="Is personal information retained only for as long as the purpose requires?",
                remediation="Adopt and enforce retention periods per category of information.",
            ),
            ChecklistItem(
                id="ps-4",
                question="Is a retention and destruction schedule documented and applied?",
                remediation="Create a retention schedule and a secure destruction process.",
            ),
        ),
    ),
    Condition(
        slug="further_processing_limitation",
        name="Further Processing Limitation",
        act_reference="s.14",
        description=(
            "Further processing of personal information must be compatible with the "
            "purpose for which it was originally collected."
        ),
        checklist=(
            ChecklistItem(
                id="fp-1",
                question="Is further processing checked for compatibility with the original purpose?",
                remediation="Document a compatibility assessment before any new use of existing data.",
            ),
            ChecklistItem(
                id="fp-2",
                question="Are new or changed purposes communicated to data subjects before processing begins?",
                remediation=(
                    "Notify data subjects and obtain consent where a new purpose is "
                    "not compatible with the original one."
                ),
            ),
            ChecklistItem(
                id="fp-3",
                question="Are internal policies in place that prevent reuse of data for unrelated purposes?",
                remediation="Adopt a data-use policy that governs reuse and secondary processing.",
            ),
            ChecklistItem(
                id="fp-4",
                question="Is de-identified data used for secondary purposes such as analytics and research?",
                remediation="Prefer de-identified data for analytics, research and testing.",
            ),
        ),
    ),
    Condition(
        slug="information_quality",
        name="Information Quality",
        act_reference="s.15",
        description=(
            "The responsible party must take reasonably practicable steps to ensure "
            "that personal information is complete, accurate, not misleading and "
            "updated where necessary."
        ),
        checklist=(
            ChecklistItem(
                id="iq-1",
                question="Are steps taken to ensure personal information is accurate and not misleading?",
                remediation="Add verification steps at collection and at update points.",
            ),
            ChecklistItem(
                id="iq-2",
                question="Is there a process for data subjects to update or correct their information?",
                remediation="Publish a correction-request procedure and honour requests timeously.",
            ),
            ChecklistItem(
                id="iq-3",
                question="Are records reviewed and corrected when errors are discovered?",
                remediation="Create an error-correction workflow and log corrections.",
            ),
            ChecklistItem(
                id="iq-4",
                question="Is out-of-date information updated or removed where the purpose requires it?",
                remediation="Apply the retention schedule and refresh stale records.",
            ),
        ),
    ),
    Condition(
        slug="openness",
        name="Openness",
        act_reference="s.16-17",
        description=(
            "The responsible party must document its processing operations and notify "
            "data subjects, and where required the Information Regulator, of what it "
            "does with personal information."
        ),
        checklist=(
            ChecklistItem(
                id="op-1",
                question="Is a PAIA manual (section 51) prepared, maintained and made available?",
                remediation="Publish the PAIA manual and update it when processing changes.",
            ),
            ChecklistItem(
                id="op-2",
                question="Is a privacy policy published explaining what personal information is collected and why?",
                remediation="Publish a plain-language privacy policy at collection points and on your website.",
            ),
            ChecklistItem(
                id="op-3",
                question="Are data subjects notified of the identity of the responsible party and the purpose of processing?",
                remediation="Include responsible-party identity and purpose in all notices.",
            ),
            ChecklistItem(
                id="op-4",
                question="Has the Information Regulator been notified of processing operations where required?",
                remediation="Confirm whether notification or registration obligations apply to your organisation.",
            ),
            ChecklistItem(
                id="op-5",
                question="Are processing operations documented and available for inspection?",
                remediation="Maintain the record of processing activities and make it available on request.",
            ),
        ),
    ),
    Condition(
        slug="security_safeguards",
        name="Security Safeguards",
        act_reference="s.19-22",
        description=(
            "The responsible party must secure the integrity and confidentiality of "
            "personal information by taking appropriate, reasonable technical and "
            "organisational measures against loss, damage, destruction and unlawful "
            "access."
        ),
        checklist=(
            ChecklistItem(
                id="ss-1",
                question="Are appropriate technical safeguards (access control, encryption, network protection) in place?",
                remediation="Apply access control, encryption in transit and at rest, and network protections.",
            ),
            ChecklistItem(
                id="ss-2",
                question="Are appropriate organisational measures (policies, training, confidentiality) in place?",
                remediation="Implement a security policy, staff training and confidentiality obligations.",
            ),
            ChecklistItem(
                id="ss-3",
                question="Is a security incident and breach response plan in place?",
                remediation="Draft a breach response plan with roles and the 72-hour notification procedure.",
            ),
            ChecklistItem(
                id="ss-4",
                question="Are security measures tested and reviewed regularly?",
                remediation="Run periodic security reviews, tests and vulnerability assessments.",
            ),
            ChecklistItem(
                id="ss-5",
                question="Are processors contractually required to maintain security safeguards?",
                remediation="Include security obligations in processing agreements.",
            ),
            ChecklistItem(
                id="ss-6",
                question="Are breaches notified to the Regulator within 72 hours and to data subjects where harm is likely?",
                remediation=(
                    "Follow the section 22 notification duties and log every breach in "
                    "the breach register."
                ),
            ),
        ),
    ),
    Condition(
        slug="data_subject_participation",
        name="Data Subject Participation",
        act_reference="s.23-25",
        description=(
            "Data subjects may request access to their personal information, and may "
            "request correction or deletion of information that is inaccurate, "
            "irrelevant, excessive or unlawfully obtained."
        ),
        checklist=(
            ChecklistItem(
                id="ds-1",
                question="Is there a procedure for data subjects to request access to their personal information?",
                remediation="Document and publish the access-request procedure (PAIA manual).",
            ),
            ChecklistItem(
                id="ds-2",
                question="Are access requests handled within the statutory timeframes?",
                remediation="Track requests and respond within 30 days as the PAIA provides.",
            ),
            ChecklistItem(
                id="ds-3",
                question="Is there a procedure for data subjects to request correction or deletion of their information?",
                remediation="Publish a correction and deletion request process.",
            ),
            ChecklistItem(
                id="ds-4",
                question="Are refusals of access or correction communicated with reasons and appeal guidance?",
                remediation="Give written reasons and inform data subjects of their remedies.",
            ),
        ),
    ),
)

CONDITION_MAP: dict[str, Condition] = {c.slug: c for c in CONDITIONS}

ALL_ITEM_IDS: tuple[str, ...] = tuple(
    item.id for condition in CONDITIONS for item in condition.checklist
)


def get_condition(slug: str) -> Condition:
    """Return the condition with the given slug, raising KeyError if unknown."""
    return CONDITION_MAP[slug]


def item_lookup() -> dict[str, tuple[str, str, ChecklistItem]]:
    """Map every checklist item id to (condition slug, condition name, item).

    Useful for the interactive questionnaire and for answer validation.
    """
    lookup: dict[str, tuple[str, str, ChecklistItem]] = {}
    for condition in CONDITIONS:
        for item in condition.checklist:
            lookup[item.id] = (condition.slug, condition.name, item)
    return lookup
