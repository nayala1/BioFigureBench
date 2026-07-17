# BioReasonBench v0.2.0 — Figure Interpretation Pilot

BioReasonBench v0.2.0 is a focused five-case pilot for evaluating how
multimodal AI models interpret biological figures and reason about
life-sciences evidence.

The current release assesses whether models can identify experimental
controls, distinguish observations from conclusions, calibrate claims to the
available evidence, avoid unsupported scientific interpretations, and
recommend informative follow-up experiments.

BioReasonBench is currently distributed through the `biofigurebench` Python
package and command-line interface.

## Included

- Five curated biological figure-interpretation cases spanning quantitative
  microscopy, neurodevelopment, single-cell genomics, functional genomics,
  and preclinical therapeutics.
- A reproducible Python pipeline for dataset validation, multimodal model
  evaluation, structured response capture, automated scoring, and reporting.
- Claude Sonnet 5 baseline evaluation results, including model responses,
  per-case scores, latency metrics, and an interactive HTML report.
- A provisional domain-expert review conducted by a single reviewer,
  comparing automated concept-coverage scores with biological interpretation
  accuracy.
- Automated tests and documented workflows for reproducing or extending the
  benchmark.

## Pilot results

- All five benchmark cases completed successfully.
- Mean automated concept-coverage score: 59.6/100.
- Provisional mean domain-expert score: 82.6/100.
- Mean model latency: 20.23 seconds per case.
- Claude generally showed strong control identification, evidence calibration,
  and restraint around unsupported mechanistic claims.
- The clearest failure involved panel-level interpretation of neuronal
  morphology in BFB-002.

## Key finding

The automated scorer was useful for determining whether expected concepts
were present in each response, but it under-scored biologically correct
answers expressed in different wording and missed some panel-specific
interpretation errors identified during expert review.

Automated scores should therefore be treated as measures of concept coverage
rather than standalone measures of biological accuracy.

## Limitations

- The current release contains five cases and is intended as a pilot.
- The v0.2.0 release evaluates biological figure interpretation only.
- Baseline results were generated using one model.
- Expert assessment was conducted by one reviewer and was not blinded.
- Automated scoring does not replace domain-expert evaluation of biological
  accuracy.
- The benchmark does not yet support formal claims about comparative model
  performance.

## Future scope

BioReasonBench is intended to support additional life-sciences reasoning
tracks in future releases. These tracks are not included in v0.2.0.
