"""Additional compliance documents: operator agreement, DSR form,
consent template, retention schedule, and PIA questionnaire.

Each generator builds a real, ready-to-edit markdown document from a
:class:`~gavaza.config.Company` using plain Python string templates.
"""

from __future__ import annotations

from gavaza.config import Company


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


def generate_operator_agreement(company: Company) -> str:
    """Generate an operator (processor) agreement template as markdown.

    The template implements the operator obligations of sections 20 and
    21 of POPIA: documented instructions, confidentiality, security
    measures, breach notification, assistance with data subject rights,
    sub-operator consent, records, and return or destruction on
    termination.
    """
    return f"""# Operator Agreement — {company.name}

This agreement sets out the obligations of an operator (processor) that
processes personal information on behalf of {company.name} (the
responsible party) under the Protection of Personal Information Act 4 of
2013 ("POPIA").

## Parties

- **Responsible party:** {company.name}
- **Operator:** [name of the operator]
- **Date:** [date]

## 1. Processing instructions

The operator must process personal information only on the documented
instructions of the responsible party. The operator must never process
personal information for its own purposes.

## 2. Confidentiality

The operator must ensure that every person authorised to process the
personal information commits to confidentiality. Access must be limited
to persons with a need to process.

## 3. Security measures

The operator must implement appropriate technical and organisational
measures to secure the personal information against loss, damage,
destruction, and unlawful access or processing. The measures must match
or exceed the safeguards documented in the responsible party's
compliance programme.

## 4. Breach notification

The operator must notify the responsible party immediately after
becoming aware of any security compromise or breach involving the
personal information. The notice must describe the nature of the breach,
the categories and volume of information involved, and the measures
taken or proposed.

## 5. Assistance with data subject rights

The operator must assist the responsible party to respond to requests
from data subjects to access, correct, delete, or object to the
processing of their personal information.

## 6. Sub-operators

The operator must not engage a sub-operator without the prior written
consent of the responsible party. Each sub-operator must be bound by
obligations at least as protective as this agreement.

## 7. Records

The operator must maintain records of processing activities performed
under this agreement and make them available for audit by the
responsible party on reasonable notice.

## 8. Termination

On termination of this agreement, the operator must, at the choice of
the responsible party, return or securely destroy the personal
information and certify the destruction.

## Contact

{_company_block(company)}

_This template was generated with Gavaza on a best-effort basis and
should be reviewed by a qualified professional before use._
"""


def generate_dsr_form(company: Company) -> str:
    """Generate a data subject request form template as markdown."""
    return f"""# Data Subject Request Form — {company.name}

Use this form to exercise your rights under the Protection of Personal
Information Act 4 of 2013 ("POPIA"). Submit the completed form to the
Information Officer using the contact details at the end.

## Your details

- **Full name:**
- **Identity or passport number:**
- **Email address:**
- **Telephone number:**
- **Postal address:**

## The right you are exercising

Select one or more:

- [ ] **Access** (section 23) — confirm whether we hold your personal
  information and request a copy of it.
- [ ] **Correction** (section 24) — correct or delete personal
  information that is inaccurate, misleading, or incomplete.
- [ ] **Objection** (section 25) — object to the processing of your
  personal information on reasonable grounds.
- [ ] **Withdrawal of consent** — withdraw consent where processing is
  based on your consent.

## Information the request relates to

Describe the personal information or processing activity the request
concerns, and the time period if known:

[describe the information]

## How you want us to respond

- [ ] Provide a copy by email
- [ ] Provide a copy by post
- [ ] Confirm that the correction or deletion was completed
- [ ] Confirm that processing has stopped

## Declaration

I confirm that the information in this form is accurate and that I am
the data subject, or that I am authorised to act on behalf of the data
subject.

- **Signature:**
- **Date:**

## Contact for requests

{_company_block(company)}

The Information Officer will respond within a reasonable time; the
Information Regulator's guidance uses 30 days from receipt.
"""


def generate_consent_template(company: Company) -> str:
    """Generate a consent clause template as markdown."""
    return f"""# Consent Clause Template — {company.name}

Use this clause when consent is the lawful basis for processing. Consent
under POPIA must be freely given, specific, and informed. Copy the
relevant sections into your forms, websites, or contracts and complete
the placeholders.

## 1. Standard consent clause

By signing below, I consent to {company.name} processing my personal
information for the following specific purpose(s):

- [purpose 1]
- [purpose 2]

I understand that:

1. The information collected is limited to what is necessary for these
   purposes.
2. My consent is voluntary and I may withdraw it at any time.
3. Withdrawal does not affect the lawfulness of processing before the
   withdrawal.
4. My information will not be shared with third parties except as set
   out in the privacy policy.

- **Name:**
- **Signature:**
- **Date:**
- **Consent channel:** [website form / in-person / email / telephone]

## 2. Special personal information clause

Where the processing involves special personal information (such as
health, biometric, or criminal behaviour data), consent must be explicit:

I explicitly consent to {company.name} processing my special personal
information, namely [categories], for the purpose of [purpose].

- **Name:**
- **Signature:**
- **Date:**

## 3. Withdrawal instructions

To withdraw consent, contact the Information Officer:

{_company_block(company)}

We will stop the processing described in this consent and confirm the
withdrawal within a reasonable time.
"""


def generate_retention_schedule(company: Company) -> str:
    """Generate a records retention schedule template as markdown."""
    return f"""# Records Retention Schedule — {company.name}

This schedule sets out how long {company.name} keeps each category of
records and how they are disposed of. It supports the information
quality condition (POPIA section 16) and the requirement to keep
records only as long as necessary.

## Retention periods

| Record category | Examples | Retention period | Lawful basis | Disposal |
|---|---|---|---|---|
| Employee records | Contracts, payroll, leave | 5 years after termination | Labour law; tax law | Secure shredding |
| Financial records | Invoices, bank statements, tax | 7 years | Tax Act; prescription | Secure shredding |
| Customer records | Contracts, support history | 5 years after last activity | Contract; legitimate interest | De-identification |
| Marketing records | Consent records, preferences | Until consent is withdrawn | Consent | Deletion |
| Recruitment records | CVs, interview notes | 6 months after decision | Legitimate interest; consent | Deletion |
| Security logs | Access logs, incident reports | 2 years | Security safeguards | Deletion |
| Data subject requests | Request forms, responses | 5 years after completion | Legal obligation | Secure shredding |

## Review

This schedule is reviewed at least annually by the Information Officer.
Records are disposed of by secure shredding for paper, secure deletion
for electronic files, and de-identification where retention of the
underlying data is still required.

## Responsibility

The Information Officer is responsible for enforcing this schedule.

{_company_block(company)}
"""


def generate_pia_questionnaire(company: Company) -> str:
    """Generate a privacy impact assessment questionnaire as markdown."""
    return f"""# Privacy Impact Assessment Questionnaire — {company.name}

Complete this questionnaire before starting any processing activity that
may pose a high risk to the rights of data subjects (POPIA section 8 and
the accountability condition). The Information Officer reviews the
answers and decides whether the activity may proceed and under what
conditions.

## 1. Activity overview

1. Describe the processing activity in one paragraph.
2. What personal information categories are involved?
3. Does the activity involve special personal information (health,
   biometric, criminal behaviour, or other special categories)?
4. Does the activity involve the personal information of children?

## 2. Necessity and proportionality

5. What is the purpose of the processing?
6. What lawful basis justifies the processing?
7. Can the purpose be achieved with less personal information?
8. What happens if the activity does not proceed?

## 3. Data subject impact

9. Could the processing cause harm, distress, or disadvantage to data
   subjects?
10. Could the processing lead to decisions that affect data subjects'
    legal rights?
11. Are data subjects likely to expect this processing?

## 4. Transfers and sharing

12. Will personal information be shared with third parties?
13. Will personal information be transferred outside South Africa? To
    which country, and under what safeguard?

## 5. Security and retention

14. What technical and organisational measures protect the information?
15. How long will the information be kept, and how is it disposed of?

## 6. Rights and transparency

16. How will data subjects be informed about this processing?
17. How will data subjects exercise access, correction, and objection
    rights?

## 7. Decision

- [ ] Approved as described
- [ ] Approved with conditions (list them)
- [ ] Rejected

- **Completed by:**
- **Reviewed by (Information Officer):**
- **Date:**

{_company_block(company)}
"""
