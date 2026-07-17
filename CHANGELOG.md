# Changelog

## 0.2.0 — BioReasonBench Figure Interpretation pilot

- Renamed the public project to BioReasonBench for the first public release,
  while preserving the internal `biofigurebench` package and CLI.
- Positioned the release as the Biological Figure Interpretation pilot
  developed from the earlier BioFigureBench working project.

- Corrected BFB-002 to distinguish DD/VD and DA/DB reporters and all panel groups.
- Removed unsupported penetrance language from the BFB-002 reference conclusion.
- Replaced whole-response keyword scoring with field-specific concept coverage.
- Added explicit case-specific contradiction checks.
- Added resumable, incremental all-case execution to prevent duplicate API charges.
- Added retry and continue-on-error behavior.
- Added a single `pipeline` command for all five cases, scoring, metrics, and HTML reporting.
- Added optional expert-score integration and automated–expert discrepancy reporting.
- Added tests covering all five cases, field scoping, contradiction penalties, and reporting.

## 0.1.0

- Initial five-case benchmark MVP.
