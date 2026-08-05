# Gavaza

**POPIA compliance toolkit for South African organisations.**

Gavaza models the eight conditions for the lawful processing of personal
information under the **Protection of Personal Information Act 4 of 2013
(POPIA)**, runs a compliance assessment against them, and generates the
documents a responsible party needs:

- **PAIA manual** (section 51 of the Promotion of Access to Information
  Act 2 of 2000) — purpose, company details, Information Officer, records
  held, request procedure, fees, grounds for refusal and contact.
- **Privacy policy** — who we are, what we collect, why, sharing, security,
  retention, rights and contact.
- **Record of processing activities** — a register of processing activities
  with purpose, data subjects, categories, retention, lawful basis and sharing.
- **Breach register** (CSV) plus the **72-hour breach notification checklist**
  and timeline guide under section 22.

Gavaza is a tool, **not legal advice**. Documents it generates are starting
points that should be reviewed by a qualified professional before use.

- Pure Python 3.11+ standard library — no runtime dependencies.
- Local-first: all data lives in `~/.gavaza/` (override with `GAVAZA_HOME`).
- MIT licensed. Part of the Enternovate constellation of open-source tools.

## The eight POPIA conditions

| # | Condition | POPIA | What it means in plain language |
|---|-----------|-------|--------------------------------|
| 1 | Accountability | s.8 | You must comply and be able to prove compliance to the Information Regulator. |
| 2 | Processing Limitation | s.9–11 | Process lawfully, minimally, and only with consent or another lawful basis. |
| 3 | Purpose Specification | s.13 | Collect for a specific, defined, lawful purpose and tell data subjects what it is. |
| 4 | Further Processing Limitation | s.14 | Any further use must be compatible with the original purpose. |
| 5 | Information Quality | s.15 | Keep personal information complete, accurate, not misleading and current. |
| 6 | Openness | s.16–17 | Document your processing operations and notify data subjects and the Regulator. |
| 7 | Security Safeguards | s.19–22 | Apply reasonable technical and organisational measures; notify breaches within 72 hours. |
| 8 | Data Subject Participation | s.23–25 | Let data subjects access their information and request correction or deletion. |

Each condition carries a checklist of 4–6 questions with remediation hints —
the questions drive the assessment questionnaire.

## Installation

```bash
pip install gavaza          # once published
# or from a checkout:
pip install -e .
```

Python 3.11 or newer. No external dependencies.

## Quick start

```bash
# 1. Create your company configuration
gavaza init --name "Acme (Pty) Ltd" --reg "2020/123456/07" \
  --email info@acme.co.za --info-officer "Jane Dlamini" --contact "+27 11 555 0100"

# or from an existing JSON file
gavaza init company.json

# 2. Run the compliance assessment (all items, scripted answers)
gavaza assess --answers answers.json
# ...or interactively
gavaza assess --interactive

# 3. Generate the documents
gavaza generate --docs all

# 4. Produce a report
gavaza report --format md --out report.md
gavaza report --format html --out report.html
gavaza report --format json --out report.json
```

Scripted answers are a JSON object mapping checklist item ids to
`"yes"`, `"no"` or `"partial"` (or to `{"value": ..., "note": ...}`):

```json
{
  "acc-1": "yes",
  "acc-2": {"value": "partial", "note": "policy drafted, not yet approved"},
  "pl-1": "no"
}
```

Run `gavaza conditions` to list every condition and checklist item id.

## CLI reference

```
gavaza --version
gavaza conditions                                  list the 8 conditions + checklists
gavaza init [company.json] [--name .. --reg .. --email .. --address .. --info-officer .. --contact ..]
gavaza assess [--interactive] [--answers FILE] [--out FILE]
gavaza report [--format json|md|html] [--out FILE] [--results FILE]
gavaza generate [--docs paia|privacy|register|all] [--out DIR]
gavaza breach add --description .. [--date .. --categories .. --affected N --risk .. --status ..]
gavaza breach list
gavaza breach timeline
```

## Data and outputs

Everything is stored under the Gavaza data directory — `~/.gavaza/` by
default, or the path in the `GAVAZA_HOME` environment variable:

```
~/.gavaza/
├── company.json                          # company configuration
├── assessment.json                       # latest assessment results + scores
├── breach-register.csv                   # breach register (CSV)
└── docs/                                 # generated documents (default --out)
    ├── PAIA-manual.md
    ├── privacy-policy.md
    └── record-of-processing-activities.md
```

### Scoring

- Each answer scores: `yes` = 100, `partial` = 50, `no`/unanswered = 0.
- A condition's score is the mean of its checklist item scores (0–100).
- The overall score is the mean of the eight condition scores.
- Grade: A ≥ 90, B ≥ 80, C ≥ 70, D ≥ 60, E ≥ 50, F < 50.
- Reports include a prioritised remediation list (worst-scoring conditions
  first, with actionable hints).

## Development

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -q
ruff check src tests
```

CI runs pytest on Python 3.11 and 3.12 plus ruff (see
`.github/workflows/ci.yml`).

## Licence

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Enternovate (Pty) Ltd.

## Constellation

Gavaza is part of the Enternovate constellation of open-source, local-first
developer tools. See the [Enternovate organisation](https://github.com/enternovate)
for sibling projects. Gavaza is not affiliated with, or endorsed by, the
South African Information Regulator.
