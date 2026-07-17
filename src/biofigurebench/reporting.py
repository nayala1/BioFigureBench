from __future__ import annotations

import csv
import html
import json
from pathlib import Path
from statistics import mean

from .models import BenchmarkCase, ModelResponse, ScoreBreakdown


def _fmt(value: float | None, digits: int = 1) -> str:
    return "—" if value is None else f"{value:.{digits}f}"


def _bar(value: float, label: str) -> str:
    width = max(0.0, min(100.0, value))
    return (
        '<div class="bar-row">'
        f'<span class="bar-label">{html.escape(label)}</span>'
        '<div class="bar-track">'
        f'<div class="bar-fill" style="width:{width:.1f}%"></div>'
        "</div>"
        f'<span class="bar-value">{value:.1f}</span>'
        "</div>"
    )


def _load_expert_reviews(path: str | Path | None) -> dict[tuple[str, str], dict[str, str]]:
    if not path:
        return {}
    source = Path(path)
    if not source.exists():
        return {}
    rows: dict[tuple[str, str], dict[str, str]] = {}
    with source.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            expert_total = row.get("expert_total_0_100") or row.get("expert_score")
            if row.get("case_id") and row.get("model") and expert_total:
                normalized = dict(row)
                normalized["expert_total_0_100"] = expert_total
                rows[(row["case_id"], row["model"])] = normalized
    return rows


def write_report(
    *,
    cases: list[BenchmarkCase],
    responses: list[ModelResponse],
    scores: list[ScoreBreakdown],
    output: str | Path,
    metrics_output: str | Path | None = None,
    expert_reviews: str | Path | None = None,
) -> None:
    case_map = {case.case_id: case for case in cases}
    response_map = {(r.case_id, r.model): r for r in responses}
    expert_map = _load_expert_reviews(expert_reviews)

    evaluated_ids = {score.case_id for score in scores}
    missing_cases = [case.case_id for case in cases if case.case_id not in evaluated_ids]
    latencies = [r.latency_seconds for r in responses if r.latency_seconds is not None]
    totals = [score.total_score for score in scores]
    field_coverages = [score.field_concept_coverage for score in scores]
    claim_safety = [score.claim_safety for score in scores]

    metrics = {
        "benchmark_cases": len(cases),
        "evaluated_cases": len(evaluated_ids),
        "coverage_percent": round(100 * len(evaluated_ids) / len(cases), 1) if cases else 0.0,
        "missing_cases": missing_cases,
        "models": sorted({score.model for score in scores}),
        "mean_automated_score": round(mean(totals), 1) if totals else None,
        "mean_field_concept_coverage": round(mean(field_coverages), 1) if field_coverages else None,
        "mean_claim_safety": round(mean(claim_safety), 1) if claim_safety else None,
        "mean_latency_seconds": round(mean(latencies), 2) if latencies else None,
        "total_latency_seconds": round(sum(latencies), 2) if latencies else None,
    }

    score_rows = []
    case_sections = []
    chart_rows = []
    for score in scores:
        case = case_map[score.case_id]
        response = response_map.get((score.case_id, score.model))
        expert = expert_map.get((score.case_id, score.model))
        expert_total = float(expert["expert_total_0_100"]) if expert else None
        delta = score.total_score - expert_total if expert_total is not None else None
        chart_rows.append(_bar(score.total_score, score.case_id))
        score_rows.append(
            "<tr>"
            f"<td>{html.escape(score.case_id)}</td>"
            f"<td>{html.escape(case.title)}</td>"
            f"<td>{html.escape(score.model)}</td>"
            f"<td>{score.total_score:.1f}</td>"
            f"<td>{score.field_concept_coverage:.1f}</td>"
            f"<td>{score.claim_safety:.1f}</td>"
            f"<td>{_fmt(response.latency_seconds if response else None, 2)}</td>"
            f"<td>{_fmt(expert_total)}</td>"
            f"<td>{_fmt(delta)}</td>"
            "</tr>"
        )

        field_rows = "".join(
            f"<tr><td>{html.escape(field)}</td><td>{value:.1f}</td>"
            f"<td>{html.escape('; '.join(score.missing_field_concepts.get(field, [])) or 'None')}</td></tr>"
            for field, value in score.field_scores.items()
        )
        triggered = score.triggered_prohibited_claims + score.triggered_contradictions
        case_sections.append(
            f"<section class='case-card'><h3>{html.escape(score.case_id)} — {html.escape(case.title)}</h3>"
            f"<p><strong>Domain:</strong> {html.escape(case.domain)} &nbsp; "
            f"<strong>Difficulty:</strong> {html.escape(case.difficulty)}</p>"
            f"<p><strong>Automated rubric score:</strong> {score.total_score:.1f}/100</p>"
            "<table><thead><tr><th>Response field</th><th>Coverage</th><th>Missing concepts</th></tr></thead>"
            f"<tbody>{field_rows}</tbody></table>"
            f"<p><strong>Triggered claims/contradictions:</strong> {html.escape('; '.join(triggered) or 'None')}</p>"
            f"<details><summary>Model response</summary><pre>{html.escape(json.dumps(response.answer.model_dump(), indent=2) if response else 'Missing')}</pre></details>"
            "</section>"
        )

    css = """
    body{font-family:Arial,sans-serif;max-width:1200px;margin:0 auto;padding:32px;color:#202124;background:#f7f8fa}
    h1,h2,h3{color:#17233c} .subtitle{color:#5f6368}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin:20px 0}
    .metric,.case-card,.chart{background:white;border:1px solid #dfe3ea;border-radius:10px;padding:18px;box-shadow:0 1px 2px rgba(0,0,0,.04)}
    .metric .value{font-size:28px;font-weight:700;margin-top:8px}.metric .label{color:#5f6368;font-size:13px;text-transform:uppercase}
    table{border-collapse:collapse;width:100%;background:white;margin:12px 0 22px}th,td{border:1px solid #dfe3ea;padding:9px;text-align:left;vertical-align:top}th{background:#eef2f7}
    .bar-row{display:grid;grid-template-columns:80px 1fr 52px;gap:10px;align-items:center;margin:10px 0}.bar-track{height:16px;background:#e8ebef;border-radius:8px;overflow:hidden}.bar-fill{height:100%;background:#61758a}.bar-value{text-align:right;font-variant-numeric:tabular-nums}.bar-label{font-weight:600}
    .warning{background:#fff6df;border-left:4px solid #d79b00;padding:12px 16px;margin:18px 0}.case-card{margin:18px 0}pre{white-space:pre-wrap;word-break:break-word;background:#f4f6f8;padding:12px;border-radius:6px}
    """
    coverage_warning = (
        ""
        if not missing_cases
        else f"<div class='warning'><strong>Incomplete run:</strong> Missing cases: {html.escape(', '.join(missing_cases))}</div>"
    )
    report = f"""<!doctype html><html><head><meta charset='utf-8'><title>BioReasonBench Biological Figure Interpretation Pilot Report</title><style>{css}</style></head>
    <body><h1>BioReasonBench Biological Figure Interpretation Pilot Report</h1><p class='subtitle'>Five-case Biological Figure Interpretation pilot summary. Automated scores are rubric proxies and should not be presented as expert biological-accuracy scores.</p>
    {coverage_warning}
    <div class='grid'>
      <div class='metric'><div class='label'>Cases evaluated</div><div class='value'>{metrics['evaluated_cases']}/{metrics['benchmark_cases']}</div></div>
      <div class='metric'><div class='label'>Mean automated score</div><div class='value'>{_fmt(metrics['mean_automated_score'])}</div></div>
      <div class='metric'><div class='label'>Mean field coverage</div><div class='value'>{_fmt(metrics['mean_field_concept_coverage'])}%</div></div>
      <div class='metric'><div class='label'>Mean claim safety</div><div class='value'>{_fmt(metrics['mean_claim_safety'])}%</div></div>
      <div class='metric'><div class='label'>Mean latency</div><div class='value'>{_fmt(metrics['mean_latency_seconds'],2)} s</div></div>
    </div>
    <div class='chart'><h2>Automated score by case</h2>{''.join(chart_rows)}</div>
    <h2>Run-level metrics</h2><table><thead><tr><th>Case</th><th>Title</th><th>Model</th><th>Automated score</th><th>Field coverage</th><th>Claim safety</th><th>Latency (s)</th><th>Expert score</th><th>Auto–expert delta</th></tr></thead><tbody>{''.join(score_rows)}</tbody></table>
    <h2>Case details</h2>{''.join(case_sections)}
    <div class='warning'><strong>Interpretation note:</strong> The automated score checks field-specific concept coverage and explicit contradictions. Expert review remains necessary for subtle panel-level visual errors.</div>
    </body></html>"""

    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(report, encoding="utf-8")
    if metrics_output:
        metrics_path = Path(metrics_output)
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
