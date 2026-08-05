"""Document generators: PAIA manual, privacy policy and record of processing.

Each generator builds a real, ready-to-edit markdown document from a
:class:`~gavaza.config.Company` using plain Python string templates — no
external template engine. The breach register is a CSV handled by
:mod:`gavaza.breach`.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

from gavaza.config import Company

DEFAULT_PROCESSING_ACTIVITIES: tuple[dict[str, str], ...] = (
    {
        "activity": "Employee administration",
        "purpose": "Manage employment contracts, payroll and leave",
        "data_subjects": "Employees",
        "categories": "Names, identity numbers, bank details, contact details",
        "retention": "5 years after termination of employment",
        "lawful_basis": "Contract performance; legal obligation (tax and labour law)",
        "sharing": "SARS, banks, medical aid and retirement funds",
    },
    {
        "activity": "Customer account management",
        "purpose": "Provide products and services, billing and support",
        "data_subjects": "Customers",
        "categories": "Names, contact details, delivery addresses, transaction history",
        "retention": "7 years for financial records (prescription)",
        "lawful_basis": "Contract performance; legitimate interest",
        "sharing": "Payment processors, couriers, accountants",
    },
    {
        "activity": "Marketing communications",
        "purpose": "Send newsletters and promotional offers with consent",
        "data_subjects": "Prospects and customers",
        "categories": "Names, email addresses, preferences",
        "retention": "Until consent is withdrawn",
        "lawful_basis": "Consent",
        "sharing": "Email marketing platform (processor)",
    },
    {
        "activity": "Supplier and vendor management",
        "purpose": "Procure goods and services and manage supplier accounts",
        "data_subjects": "Supplier representatives",
        "categories": "Names, business contact details, banking details",
        "retention": "5 years after the last transaction",
        "lawful_basis": "Contract performance",
        "sharing": "Banks, auditors",
    },
    {
        "activity": "Recruitment and hiring",
        "purpose": "Evaluate applicants and manage the hiring process",
        "data_subjects": "Job applicants",
        "categories": "Names, contact details, CVs, references, interview notes",
        "retention": "6 months for unsuccessful applicants (with consent)",
        "lawful_basis": "Legitimate interest; consent for retention",
        "sharing": "Background-check providers (with consent)",
    },
)


def _company_block(company: Company) -> str:
    """Render the standard company-details block used in several documents."""
    lines = [f"- **Name:** {company.name}"]
    if company.reg_no:
        lines.append(f"- **Registration number:** {company.reg_no}")
    if company.address:
        lines.append(f"- **Registered address:** {company.address}")
    if company.email:
        lines.append(f"- **Email:** {company.email}")
    if company.info_officer:
        lines.append(f"- **Information Officer:** {company.info_officer}")
    if company.contact:
        lines.append(f"- **Contact:** {company.contact}")
    return "\n".join(lines)


def generate_paia(company: Company) -> str:
    """Generate a PAIA manual (section 51 of the Promotion of Access to
    Information Act 2 of 2000) as markdown."""
    return f"""# PAIA Manual — {company.name}

Prepared in terms of section 51 of the Promotion of Access to Information
Act 2 of 2000 ("PAIA") and the Protection of Personal Information Act 4 of
2013 ("POPIA"). This manual describes the records the company holds, the
procedure for requesting access to them, and the fees that apply.

## Purpose of this manual

This manual explains how to request access to records held by {company.name}
under PAIA, what records the company holds, how requests are processed, and
the fees payable. It also explains how to exercise rights under POPIA.

## Company details

{_company_block(company)}

## Information Officer

{company.info_officer or "The Information Officer has not yet been appointed."}
is the Information Officer of {company.name} and is responsible for receiving
and processing requests for access to records and for POPIA compliance.
Requests may be directed to:

- Email: {company.email or "not yet published"}
- Contact: {company.contact or "not yet published"}
- Address: {company.address or "not yet published"}

## Records the company holds

The records the company holds include, without limitation:

1. **Personal records** of employees, customers, prospects and suppliers —
   contact details, identification information, financial information and
   employment history.
2. **Operational records** — policies, procedures, contracts, correspondence
   and minutes.
3. **Financial records** — accounting records, tax records, invoices and
   bank statements.
4. **Technical records** — system logs, support tickets and usage data.

A full register of processing activities is maintained by the Information
Officer and is available on request.

## Request procedure

1. Complete the prescribed request form (Form C, available from the
   Information Regulator's website) or send a written request to the
   Information Officer.
2. Provide sufficient particulars to enable the Information Officer to
   identify the record requested and, where applicable, to verify your
   identity.
3. Pay the applicable request fee. The Information Officer will notify you
   of the fee before processing the request.
4. The Information Officer will respond within 30 days of receiving the
   request, or such longer period as the Act allows.

## Fees

The Information Regulator prescribes the fees payable for access to records.
Currently these are:

- Request fee: as prescribed by the Information Regulator from time to time.
- Access fee: a reasonable reproduction and preparation fee per page or per
  record, as prescribed.
- Where the preparation of the record requires more than the prescribed
  number of hours, an hourly fee may be charged.

The Information Officer will confirm the applicable fees when a request is
received. No fee is payable for a request for your own personal information
that simply requires correction.

## Grounds for refusal

Access to a record may be refused on the grounds listed in sections 33 to 44
of PAIA, including where the record:

- contains personal information of a third party (unless consent or another
  ground applies);
- is protected by legal professional privilege;
- would prejudice the security or commercial operations of {company.name};
- would prejudice the safety of an individual; or
- is subject to another law that prohibits disclosure.

Where a request is refused, written reasons will be provided and you will be
informed of your right to apply to a court for relief, or to lodge a
complaint with the Information Regulator.

## Contact

For any queries about this manual, access requests or privacy matters,
contact the Information Officer:

{_company_block(company)}
"""


def generate_privacy_policy(company: Company) -> str:
    """Generate a POPIA privacy policy as markdown."""
    return f"""# Privacy Policy — {company.name}

This privacy policy explains how {company.name} ("we", "us") processes
personal information in accordance with the Protection of Personal
Information Act 4 of 2013 ("POPIA").

## Who we are

{company.name} is the responsible party for the purposes of POPIA.

{_company_block(company)}

## What we collect

We collect personal information that is necessary for our functions and
activities, including:

- **Contact details** — name, email address, telephone number and physical
  address.
- **Identification information** — identity or passport numbers where
  required by law or for verification.
- **Financial information** — bank details, payment history and billing
  information.
- **Employment information** — for staff and applicants, including
  qualifications, references and employment history.
- **Technical information** — IP addresses, device information and usage
  data collected when you interact with our systems.

## Why we collect it

We process personal information for specific, lawful purposes, including:

- to provide products and services and manage customer relationships;
- to fulfil contracts and legal obligations (for example tax and labour law);
- to communicate with you and respond to enquiries;
- to send marketing communications where you have consented; and
- to maintain the security of our systems and records.

We only collect information that is adequate, relevant and not excessive for
these purposes.

## Sharing

We do not sell personal information. We share personal information only
where necessary:

- with service providers who process information on our behalf, under
  written processing agreements;
- with regulators, courts and authorities where the law requires it; and
- with professional advisers such as auditors and legal counsel.

## Security

We apply appropriate technical and organisational measures to protect
personal information against loss, damage, destruction and unlawful access,
including access controls, encryption where appropriate, staff training and
confidentiality obligations on our processors.

## Retention

We keep personal information only for as long as is necessary for the
purposes for which it was collected, or as required by law. Records are
securely destroyed or de-identified when they are no longer needed, in
line with our retention schedule.

## Your rights

Under POPIA you have the right to:

- **Access** — request confirmation of whether we hold your personal
  information and request a copy of it (see our PAIA manual).
- **Correction** — request that inaccurate, misleading or incomplete
  information be corrected or deleted.
- **Object** — object to the processing of your personal information on
  reasonable grounds, unless the law provides otherwise.
- **Withdraw consent** — where processing is based on consent, withdraw it
  at any time.
- **Complain** — lodge a complaint with the Information Regulator
  (www.inforegulator.org.za) if you believe your rights have been infringed.

To exercise any of these rights, contact our Information Officer using the
details below. We will respond within the timeframes set out in POPIA and
PAIA.

## Contact

For questions about this policy or to exercise your rights:

{_company_block(company)}

This policy was generated with Gavaza on a best-effort basis and should be
reviewed by a qualified professional before publication.
"""


def generate_processing_register(
    company: Company, activities: Iterable[dict[str, str]] | None = None
) -> str:
    """Generate a record of processing activities (register) as markdown."""
    rows = list(activities) if activities is not None else list(DEFAULT_PROCESSING_ACTIVITIES)
    lines = [
        f"# Record of Processing Activities — {company.name}",
        "",
        (
            "This register documents the processing activities of "
            f"{company.name} in terms of the conditions for lawful processing "
            "under POPIA. It is maintained by the Information Officer and "
            "reviewed at least annually."
        ),
        "",
        (
            f"_Company: {company.name} | Registration: {company.reg_no or '—'} | "
            f"Information Officer: {company.info_officer or '—'}_"
        ),
        "",
        (
            "| Activity | Purpose | Data subjects | Categories of personal information | "
            "Retention | Lawful basis | Sharing |"
        ),
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {activity} | {purpose} | {data_subjects} | {categories} | "
            "{retention} | {lawful_basis} | {sharing} |".format(**row)
        )
    lines.append("")
    lines.append("_Generated with Gavaza — review and extend before use._")
    return "\n".join(lines)


def generate_document(company: Company, doc: str, activities: Iterable[dict[str, str]] | None = None) -> str:
    """Generate one document by name: ``paia``, ``privacy`` or ``register``."""
    if doc == "paia":
        return generate_paia(company)
    if doc == "privacy":
        return generate_privacy_policy(company)
    if doc == "register":
        return generate_processing_register(company, activities)
    raise ValueError(f"unknown document: {doc!r}; expected paia, privacy or register")


DOC_FILENAMES = {
    "paia": "PAIA-manual.md",
    "privacy": "privacy-policy.md",
    "register": "record-of-processing-activities.md",
}


def write_docs(
    company: Company,
    docs: Iterable[str] = ("paia", "privacy", "register"),
    out_dir: Path | str | None = None,
    activities: Iterable[dict[str, str]] | None = None,
) -> dict[str, Path]:
    """Generate documents into ``out_dir`` (default ``./docs``).

    Returns a mapping of document name to the path of the file written.
    """
    target = Path(out_dir) if out_dir is not None else Path("docs")
    target.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    for doc in docs:
        content = generate_document(company, doc, activities)
        path = target / DOC_FILENAMES[doc]
        path.write_text(content, encoding="utf-8")
        written[doc] = path
    return written


def default_activities() -> list[dict[str, Any]]:
    """Return a copy of the default processing activities as plain dicts."""
    return [dict(row) for row in DEFAULT_PROCESSING_ACTIVITIES]
