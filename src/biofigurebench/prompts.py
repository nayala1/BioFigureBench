from __future__ import annotations

from .models import BenchmarkCase

SYSTEM_PROMPT = """You are evaluating a biological figure as a rigorous research scientist.
Separate direct observation from inference. Do not invent statistical significance, methods,
controls, sample sizes, or mechanisms. Calibrate conclusions to the evidence visible in the
figure and supplied legend excerpt. Return valid JSON only."""


def render_prompt(case: BenchmarkCase) -> str:
    return f"""CASE: {case.case_id} — {case.title}

DOMAIN: {case.domain}
CONTEXT: {case.context}
LEGEND EXCERPT: {case.legend_excerpt}

TASK:
{case.prompt}

Return JSON with exactly these fields:
{{
  "experiment": "string",
  "observations": ["string"],
  "controls_and_statistics": ["string"],
  "supported_conclusion": "string",
  "unsupported_claim": "string",
  "follow_up": "string"
}}
"""
