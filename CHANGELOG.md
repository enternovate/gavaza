# Changelog

## [0.2.0] - 2026-08-07

### Added
- six additional POPIA sections covering special personal information, children, cross-border transfers, automated decisions, direct marketing, and data subject rights
- weighted scoring with 1-5 maturity levels and gap summaries
- local evidence store with hashed file copies
- operator agreement, data subject request form, consent template, retention schedule, and privacy impact assessment questionnaire
- POPIA to GDPR mapping
- data subject request workflow with the 30-day response deadline
- CSV report export

### Changed
- document suite now has eight document types
- assessment results carry maturity data and per-condition weights

### Security
- home directory uses mode 0700
- zero-telemetry guard tests enforce no network imports
