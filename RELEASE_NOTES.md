# BioFigureBench v0.2.0 — Five-case MVP

BioFigureBench v0.2.0 is a compact public MVP for evaluating multimodal model
interpretation of biological figures and evidence-calibrated scientific
reasoning.

## Included

- Five curated figure-interpretation cases spanning cell biology and
  quantitative microscopy, neurodevelopment and C. elegans genetics,
  single-cell genomics, cancer biology and functional genomics, and preclinical
  therapeutics and drug delivery.
- Typed Python schemas for benchmark records, model responses, scoring output,
  and report metrics.
- Claude multimodal adapter for model execution.
- Resumable execution so completed case/model responses are preserved across
  interrupted runs.
- Field-specific scoring with concept-coverage checks and case-specific
  contradiction penalties.
- HTML, CSV, and JSON reporting.
- Claude Sonnet 5 baseline results for all five MVP cases.
- Provisional single-reviewer domain-expert review artifacts.

## Key Finding

The v0.2.0 pilot shows that automated lexical rubric scoring is useful for
transparent concept-coverage auditing, but it is not a biological-accuracy
score. The lexical rubric missed semantic paraphrases and did not fully capture
some panel-level biological errors that were identified during expert review.

## Baseline Summary

- Cases evaluated: 5 of 5.
- Mean automated rubric score: 59.6.
- Provisional expert mean: 82.6.
- Mean latency: 20.23 seconds.
