# BioReasonBench benchmark card

## Version

0.2.0 — Biological Figure Interpretation pilot.

## Intended use

Evaluate whether multimodal AI systems can interpret biological figures while separating direct observations, controls, supported conclusions, unsupported claims, and useful follow-up experiments.

## Cases

The release contains five openly licensed figures spanning cell microscopy, neurodevelopment, single-cell genomics, cancer functional genomics, and preclinical therapeutics.

BioReasonBench is intended as a broader life-sciences reasoning benchmark, but
the v0.2.0 release evaluates biological figure interpretation only.

## Automated scoring

The automated rubric reports:

- field-specific concept coverage
- explicit claim/contradiction safety
- structured-response completeness
- a weighted total score

Concepts are scored only within their intended response field. This prevents a model from receiving observation credit merely because it repeats the expected term in a follow-up or unsupported-claim field.

## Known limitation

The automated score remains a lexical-semantic proxy. It may miss paraphrased hallucinations and subtle panel-level errors. At least one domain-expert review should accompany any public model-comparison claim.

## Licensing

Each JSONL record includes article, DOI, figure, source URL, license, and attribution metadata. Source licenses must be preserved.
