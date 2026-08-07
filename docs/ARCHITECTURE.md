# Gavaza Architecture

Gavaza is a POPIA compliance toolkit. It models the eight conditions,
scores an assessment, and generates the documents a responsible party
needs. All data lives under the Gavaza home.

## Module map

| Module | Responsibility |
|---|---|
| `conditions.py` | The eight POPIA conditions with their checklists |
| `sections.py` | Additional POPIA sections: special information, children, cross-border, automated decisions, direct marketing, DSR rights |
| `assess.py` | The assessment engine: answers, weighted scoring, grades, maturity levels, remediation, gap summaries |
| `config.py` | Company configuration and the private home directory |
| `breach.py` | Breach register (CSV) and the 72-hour notification checklist |
| `evidence.py` | Local evidence store: hashed file copies attached to checklist items |
| `requests.py` | Data subject request workflow with the 30-day response deadline |
| `documents.py` | Operator agreement, DSR form, consent, retention, PIA generators |
| `generate.py` | PAIA, privacy policy, processing register, and document routing |
| `gdpr.py` | POPIA to GDPR mapping table |
| `report.py` | Report renderers: markdown, HTML, JSON, CSV |
| `cli.py` | The `gavaza` command surface |

## Data flow

1. `gavaza init` writes the company configuration.
2. `gavaza assess` runs the questionnaire and saves results JSON.
3. `gavaza report` renders the saved assessment.
4. `gavaza generate` produces documents from the company configuration.
5. Breaches, evidence, and requests each have their own local store.

## Privacy model

- Zero telemetry; no module imports networking primitives.
- Home directory mode 0700; stores written atomically with mode 0600.
- Documents are starting points, not legal advice.
