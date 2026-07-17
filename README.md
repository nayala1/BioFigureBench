# BioReasonBench

BioReasonBench is a reproducible benchmark for evaluating how multimodal AI
models reason through life-sciences evidence.

The v0.2.0 release contains a five-case Biological Figure Interpretation pilot
assessing whether models can interpret biological figures, identify
experimental controls, distinguish observations from conclusions, calibrate
claims to the available evidence, and propose informative follow-up
experiments.

BioReasonBench is currently distributed through the `biofigurebench` Python
package and command-line interface. The v0.2.0 release contains the Biological
Figure Interpretation pilot.

This is the first public BioReasonBench release, containing the Biological
Figure Interpretation pilot developed from the earlier BioFigureBench working
project.

Interactive report: `https://nayala1.github.io/BioReasonBench/`

## Overview

BioReasonBench is intended as a broader life-sciences reasoning benchmark. The
current v0.2.0 release is intentionally small and auditable: it evaluates
figure-grounded scientific reasoning on five curated, expert-reviewed cases.

Future benchmark tracks may evaluate other scientific reasoning tasks, but they
are not implemented in v0.2.0.

## Current Benchmark Track

The Biological Figure Interpretation pilot evaluates whether a model can:

- identify the experiment or workflow shown in a figure
- describe direct observations without over-interpreting them
- identify controls and statistical limits
- separate observations from supported conclusions
- avoid unsupported scientific claims
- propose informative follow-up experiments

## Five Biological Domains

- Cell biology and quantitative microscopy.
- Neurodevelopment and C. elegans genetics.
- Single-cell genomics.
- Cancer biology and functional genomics.
- Preclinical therapeutics and drug delivery.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev,anthropic]"
```

## Dataset Validation

Validate the final five-case dataset:

```bash
.venv/bin/biofigurebench validate --dataset data/benchmark.jsonl
```

Expected result: five cases across five biological domains.

Run tests:

```bash
.venv/bin/pytest
```

## Running The Pipeline

The canonical end-to-end command evaluates all five cases, writes each
completed response, scores available responses, and generates an HTML report:

```bash
.venv/bin/biofigurebench pipeline \
  --dataset data/benchmark.jsonl \
  --model claude-sonnet-5 \
  --output-dir results/claude-sonnet-5-final
```

Completed case/model pairs are skipped on resumed runs unless `--overwrite` is
provided.

Individual commands are also available:

```bash
.venv/bin/biofigurebench run --help
.venv/bin/biofigurebench score --help
.venv/bin/biofigurebench report --help
```

## Scoring Approach

The automated score is a field-specific lexical concept-coverage proxy. It
checks whether expected concepts appear in the intended structured response
field, whether explicit prohibited claims or contradictions are triggered, and
whether the response is complete.

The automated score is not a standalone biological-accuracy score. Expert
review remains necessary for subtle panel-level visual errors and biological
interpretation.

## Pilot Results

The included Claude Sonnet 5 baseline in
`results/claude-sonnet-5-final/` evaluated 5 of 5 cases.

- Mean automated concept-coverage score: 59.6/100.
- Provisional single-reviewer expert mean: 82.6/100.
- Mean latency: 20.23 seconds per case.

The pilot finding is that lexical scoring can make concept coverage
transparent, but it can miss semantically correct paraphrases and some
panel-level biological errors.

## Expert Review

The publication-facing expert-review artifacts are in `docs/`:

- `docs/index.html`
- `docs/expert_review_scores.csv`
- `docs/expert_review_metrics.json`

The expert review is provisional and based on a single reviewer. It is included
to show where biological judgment diverges from lexical rubric matching.

## Limitations

- The v0.2.0 release contains exactly five pilot cases.
- The current release evaluates biological figure interpretation only.
- Scores are sensitive to lexical rubric wording and do not replace biological
  expert review.
- Expert scores are provisional and single-reviewer.
- Baseline results were generated using one model.
- The benchmark does not yet support formal claims about comparative model
  performance.
- Third-party source figures remain governed by their original licenses.

## Repository Structure

```text
.
├── data/
│   └── benchmark.jsonl
├── docs/
│   ├── index.html
│   ├── expert_review_scores.csv
│   └── expert_review_metrics.json
├── results/
│   └── claude-sonnet-5-final/
│       ├── responses.jsonl
│       ├── scores.csv
│       ├── metrics.json
│       └── report.html
├── src/biofigurebench/
├── tests/
├── ATTRIBUTION.md
├── RELEASE_NOTES.md
└── README.md
```

The `docs/` files are the publication-facing expert-review report artifacts
used for GitHub Pages.

## Licensing And Attribution

BioReasonBench code and repository documentation are released under the
repository license. Third-party figures and article materials are not relicensed
by this repository.

Each benchmark item includes source, DOI, URL, license, and attribution
metadata in `data/benchmark.jsonl`. See `ATTRIBUTION.md` for additional
guidance.
