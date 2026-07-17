# BioFigureBench

BioFigureBench is a five-case MVP benchmark for evaluating multimodal AI
interpretation of biological figures. It focuses on evidence-calibrated
scientific reasoning: what a figure directly supports, what controls or
orthogonal evidence are needed, and where a model overclaims beyond the data.

Version 0.2.0 is intentionally small and auditable. It is not a comprehensive
biology benchmark; it is a polished pilot for testing figure-grounded reasoning
on curated, expert-reviewed cases.

Public report placeholder: `https://<github-user>.github.io/BioFigureBench/`

## Benchmark Domains

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

## Validation

Validate the final five-case dataset:

```bash
.venv/bin/biofigurebench validate --dataset data/benchmark.jsonl
```

Expected result: five cases across five biological domains.

Run tests:

```bash
.venv/bin/pytest
```

## Pipeline

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

## Pilot Results

The included Claude Sonnet 5 baseline in
`results/claude-sonnet-5-final/` evaluated 5 of 5 cases.

- Mean automated rubric score: 59.6.
- Provisional single-reviewer expert mean: 82.6.
- Mean latency: 20.23 seconds.

The automated score is a field-specific lexical concept-coverage proxy. It is
not a biological-accuracy score. The expert review is provisional and based on
a single reviewer; it is included to show where biological judgment diverges
from lexical rubric matching.

The pilot finding is that lexical scoring can make concept coverage
transparent, but it can miss semantic paraphrases and some panel-level
biological errors.

## Final MVP Cases

- BFB-001: label-free holotomography and organelle-identification limits.
- BFB-002: C. elegans motor-neuron tract placement, commissural laterality, and
  dorsal nerve cord continuity.
- BFB-003: single-cell nascent-RNA workflow benchmarking.
- BFB-004: in vivo single-cell CRISPR screen validation.
- BFB-005: preclinical dose-response, toxicity proxy, and translational
  calibration.

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

## Limitations

- The benchmark has exactly five MVP cases.
- Scores are sensitive to lexical rubric wording and do not replace biological
  expert review.
- Expert scores are provisional and single-reviewer.
- The benchmark evaluates figure interpretation, not broad scientific
  competence or clinical readiness.
- Third-party source figures remain governed by their original licenses.

## Licensing and Attribution

BioFigureBench code and repository documentation are released under the
repository license. Third-party figures and article materials are not relicensed
by this repository.

Each benchmark item includes source, DOI, URL, license, and attribution
metadata in `data/benchmark.jsonl`. See `ATTRIBUTION.md` for additional
guidance.
