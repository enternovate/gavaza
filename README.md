# Gavaza: POPIA Compliance Toolkit

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

POPIA is law, but the paperwork it demands is rarely the hard part. Gavaza
turns the eight conditions into a scored, repeatable assessment and produces
the documents a responsible party must keep ready: the PAIA manual, privacy
policy, records of processing, and a breach register with the 72-hour
notification checklist. Local-first, no account, no cloud.

## Key features

- **Eight-condition assessment** with weighted scoring (per-condition
  weights), an A-F grade, and 1-5 maturity levels.
- **Additional POPIA sections**: special personal information, children,
  cross-border transfers, automated decisions, direct marketing, and data
  subject rights.
- **Document suite**: PAIA manual, privacy policy, record of processing
  activities, operator agreement, data subject request form, consent
  template, retention schedule, and PIA questionnaire.
- **Breach register** (CSV) plus the **72-hour breach notification
  checklist** and timeline guide under section 22.
- **Evidence store**: attach hashed files to checklist items to demonstrate
  compliance.
- **Data subject request workflow**: intake, status tracking, and the
  30-day response deadline.
- **POPIA to GDPR mapping** for cross-border compliance analysis.
- **Reports**: markdown, HTML, JSON, and CSV exports.
- Pure Python 3.11+ standard library, no runtime dependencies.
- Local-first: all data lives in `~/.gavaza/` (override with `GAVAZA_HOME`).

## The eight POPIA conditions

1. Accountability (s.8)
2. Processing Limitation (s.9-11)
3. Purpose Specification (s.13)
4. Further Processing Limitation (s.14)
5. Information Quality (s.16)
6. Openness (s.17-18)
7. Security Safeguards (s.19-22)
8. Data Subject Participation (s.23-25)

## Install

```bash
pip install .        # from a checkout
# or directly from GitHub:
pip install git+https://github.com/enternovate/gavaza.git
```

Requires Python 3.11 or newer. No runtime dependencies.

## Quick start

```bash
gavaza init --name "Acme (Pty) Ltd" --email privacy@acme.co.za
gavaza conditions
gavaza assess --interactive
gavaza report --format md --out report.md
gavaza generate --docs all --out docs/
gavaza breach add --description "Phishing email" --affected 12
gavaza requests new --name "A. Person" --email a@example.com --right access --description "Send my records"
gavaza sections
gavaza gdpr-map
```

Expected output: each command prints the created item or the requested
reference material; `assess` prints per-condition scores, the overall
score, grade, and maturity; `report` renders the chosen format.

## CLI reference

| Command | Description |
|---|---|
| `gavaza init [--name N] [--email E] ...` | Create the company configuration |
| `gavaza assess [--interactive] [--answers FILE] [--out FILE]` | Run the questionnaire |
| `gavaza report [--format md\|html\|json\|csv] [--out FILE]` | Render the assessment report |
| `gavaza generate [--docs paia privacy register operator dsr-form consent retention pia]` | Generate documents |
| `gavaza breach add\|list\|timeline` | Manage the breach register |
| `gavaza evidence add\|list\|remove` | Manage evidence files |
| `gavaza requests new\|list\|status\|overdue` | Manage data subject requests |
| `gavaza conditions` | List the eight conditions |
| `gavaza sections [--slug S]` | List the additional sections |
| `gavaza gdpr-map [--format md\|json]` | Print the POPIA-GDPR mapping |

## How it pairs with Xavani

Xavani Agent drives Gavaza through the constellation MCP bundle
(`constellation-mcp`), which exposes `gavaza_*` tools, and through the
`gavaza-compliance` skill in `xavani-constellation-skills`. Ask Xavani to
"assess our POPIA readiness" and the CLI runs locally; nothing leaves the
machine. Assessment results and evidence can be exported to the Nyarhi
knowledge graph for long-term audit trails.

## Configuration

Copy `.env.example` to `.env` and adjust. Every variable is optional.
Gavaza runs on defaults with no configuration.

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `GAVAZA_HOME` | No | `~/.gavaza` | Data directory: config, results, docs, evidence, requests |

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest tests/ -q
```

Structure: `src/gavaza/conditions.py` (the eight conditions),
`sections.py` (additional sections), `assess.py` (scoring, maturity,
remediation), `generate.py` and `documents.py` (document suite),
`breach.py` (breach register), `evidence.py` (evidence store),
`requests.py` (DSR workflow), `gdpr.py` (mapping), `report.py`
(reports), `cli.py` (command surface).

## Testing

```bash
python -m pytest tests/ -q      # 98 tests, 0 fail / 0 skip expected
```

CI runs the suite on Python 3.11, 3.12 and 3.13 for every push and pull
request.

## Security & privacy

Zero telemetry. Gavaza never phones home; all data lives in the Gavaza
home directory you point it at. There is no cloud, no account, no
analytics. Use it offline or on an air-gapped network.

## License

MIT. See [LICENSE](LICENSE). (c) 2026 Enternovate (Pty) Ltd. Built in
South Africa.

## Contributing

Pull requests are welcome. Keep the zero-dependency rule: Gavaza must
run on the standard library alone. Tests must stay green with 0 fail
and 0 skip.

## The constellation

[Xavani](https://github.com/enternovate/xavani-agent) ·
[Nyarhi](https://github.com/enternovate/nyarhi) · Gavaza ·
[Mhangani](https://github.com/enternovate/mhangani)

Built by [Enternovate (Pty) Ltd](https://enternovate.co.za), local-first,
open, African-built.
