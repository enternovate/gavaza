# Gavaza — POPIA Compliance Toolkit

**POPIA compliance toolkit for South African organisations.**

Gavaza models the eight conditions for the lawful processing of personal
information under the **Protection of Personal Information Act 4 of 2013
(POPIA)**, runs a compliance assessment against them, and generates the
documents a responsible party needs.

![MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)
![CI](https://github.com/enternovate/gavaza/actions/workflows/ci.yml/badge.svg)

Gavaza is a tool, **not legal advice**. Documents it generates are starting
points that should be reviewed by a qualified professional before use.

## What it is / why it exists

POPIA is law — but the paperwork it demands is rarely the hard part. Gavaza
turns the eight conditions into a scored, repeatable assessment and produces
the documents a responsible party must keep ready: the PAIA manual, privacy
policy, records of processing, and a breach register with the 72-hour
notification checklist. Local-first, no account, no cloud.

## Key features

- **PAIA manual** (section 51 of the Promotion of Access to Information
  Act 2 of 2000) — purpose, company details, Information Officer, records
  held, request procedure, fees, grounds for refusal and contact.
- **Privacy policy** — who we are, what we collect, why, sharing, security,
  retention, rights and contact.
- **Record of processing activities** — a register of processing activities
  with purpose, data subjects, categories, retention, lawful basis and sharing.
- **Breach register** (CSV) plus the **72-hour breach notification checklist**
  and timeline guide under section 22.
- Pure Python 3.11+ standard library — no runtime dependencies.
- Local-first: all data lives in `~/.gavaza/` (override with `GAVAZA_HOME`).

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

Each condition carries a checklist of 4–6 questions with remediation hints.

## Install

```bash
pip install .        # from a checkout
# or directly from GitHub:
pip install git+https://github.com/enternovate/gavaza.git
```

Requires Python 3.11 or newer. No runtime dependencies.

## Quick start

```bash
gavaza init                          # create the compliance workspace
gavaza assess                        # run the 8-condition questionnaire
gavaza report                        # scored assessment with remediation
gavaza generate paia                 # PAIA manual (s51)
gavaza generate privacy              # privacy policy / POPIA notice
gavaza generate register             # record of processing activities
gavaza generate all                  # every document
gavaza breach add --description "..."  # log a breach, get the 72h checklist
gavaza conditions                    # list the eight conditions
```

## Scoring

- Each answer scores: `yes` = 100, `partial` = 50, `no`/unanswered = 0.
- A condition's score is the mean of its checklist item scores (0–100).
- The overall score is the mean of the eight condition scores.
- Grade: A ≥ 90, B ≥ 80, C ≥ 70, D ≥ 60, E ≥ 50, F < 50.
- Reports include a prioritised remediation list (worst-scoring conditions
  first, with actionable hints).

## CLI reference

| Command | Description |
|---|---|
| `gavaza init` | Create the compliance workspace |
| `gavaza assess [--answers FILE]` | Run the assessment questionnaire |
| `gavaza report [--format json\|md\|html]` | Render the scored report |
| `gavaza generate <paia\|privacy\|register\|all> [--out DIR]` | Generate compliance documents |
| `gavaza breach add --description ... [--date] [--risk] [--status]` | Log a breach + 72-hour checklist |
| `gavaza breach list` | List logged breaches |
| `gavaza breach timeline` | Print the notification timeline guide |
| `gavaza conditions` | List the eight conditions and checklists |

## How it pairs with Xavani

Ask Xavani Agent to "assess our POPIA readiness" and it loads the
`gavaza-compliance` skill (from `xavani-constellation-skills`), drives the
CLI, and explains the score. The `constellation-mcp` bundle exposes
`gavaza_assess`, `gavaza_generate`, `gavaza_breach_add`, `gavaza_breach_list`,
`gavaza_report` and `gavaza_conditions` as native tools. Pair the technical
evidence from Mhangani audits with Gavaza's security-safeguards condition to
prove compliance, not assert it.

## Configuration

Copy `.env.example` to `.env` and adjust. Every variable is optional.
Gavaza runs on defaults with no configuration.

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `GAVAZA_HOME` | No | `~/.gavaza/` | Data directory for the compliance workspace |

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest tests/ -q
ruff check src tests
```

Structure: `src/gavaza/conditions.py` (the eight conditions + checklists),
`assess.py` (scoring), `generate.py` (document rendering), `breach.py`
(register + 72-hour timeline), `report.py` (output), `cli.py` (command
surface).

## Testing

```bash
python -m pytest tests/ -q      # 63 tests, 0 fail / 0 skip expected
```

CI runs pytest on Python 3.11, 3.12 and 3.13 plus ruff (see
`.github/workflows/ci.yml`).

## Security & privacy

Zero telemetry. All data lives in `~/.gavaza/` on your machine. Gavaza never
sends documents, answers or breach records anywhere.

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Enternovate (Pty) Ltd.
Gavaza is not affiliated with, or endorsed by, the South African Information
Regulator.

## Contributing

Pull requests are welcome. Keep the zero-dependency rule: Gavaza's CLI must
run on the standard library alone. Tests must stay green (0 fail / 0 skip).

## The constellation

[Xavani](https://github.com/enternovate/xavani-agent) · [Nyarhi](https://github.com/enternovate/nyarhi) · Gavaza · [Mhangani](https://github.com/enternovate/mhangani)

Built by [Enternovate (Pty) Ltd](https://enternovate.co.za) — local-first, open, African-built.
