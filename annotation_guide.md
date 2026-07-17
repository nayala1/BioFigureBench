# Annotation and expert-review guide

For each model response, score six dimensions totaling 100 points:

- Experiment/workflow identification: 20
- Direct observation accuracy: 30
- Controls and statistical calibration: 15
- Supported conclusion: 15
- Mechanistic restraint: 10
- Follow-up value: 10

Record hallucination count, critical errors, and brief notes in `examples/human_scoring_template.csv`.

## Critical error categories

- panel misassignment
- incorrect cell or reporter identity
- invented morphology
- invented statistical significance
- mechanism inferred from phenotype alone
- unsupported superiority or clinical translation
- incorrect control assignment

## BFB-002-specific checks

- A-C use the DD/VD reporter.
- D-E assess DD/VD dorsal nerve cord continuity.
- F-G use the DA/DB reporter.
- Panel C shows an incorrect-side commissure, not a branch or loop.
- Panel E shows a dorsal nerve cord gap, not varicosities.
- Representative images do not establish penetrance.
