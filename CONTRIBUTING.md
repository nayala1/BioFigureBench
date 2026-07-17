# Contributing

## Adding a benchmark case

1. Use an openly licensed source and verify that the figure is covered by the stated license.
2. Add complete article, DOI, figure, image URL, license, and attribution metadata.
3. Write the reference answer from the displayed evidence, not from the abstract alone.
4. Include at least five required concepts and one meaningful prohibited overclaim.
5. Have a second domain expert review the case before labeling it release-ready.
6. Run `biofigurebench validate` and `pytest`.

## Annotation quality checklist

- Are all experimental groups identified correctly?
- Does the answer distinguish representative images from quantified evidence?
- Are sample size and statistical claims limited to what is displayed or stated?
- Is the supported conclusion narrower than the paper's broadest claim when appropriate?
- Would the proposed follow-up discriminate between plausible explanations?
- Is the license and attribution information complete?
