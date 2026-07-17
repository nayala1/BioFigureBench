from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .dataset import append_jsonl, load_cases, load_responses, write_jsonl
from .reporting import write_report
from .scoring import score_response

console = Console()


def cmd_validate(args: argparse.Namespace) -> None:
    cases = load_cases(args.dataset)
    domains = sorted({case.domain for case in cases})
    console.print(f"Validated [bold]{len(cases)}[/bold] cases across {len(domains)} domains.")
    for domain in domains:
        console.print(f"  • {domain}")


def _build_adapter(args: argparse.Namespace):
    if args.adapter != "anthropic":
        raise SystemExit("The final MVP currently implements only the anthropic adapter")
    try:
        from .adapters.anthropic_adapter import AnthropicAdapter
    except ModuleNotFoundError as exc:
        raise SystemExit(
            'Anthropic support is not installed. Run: pip install -e ".[dev,anthropic]"'
        ) from exc
    return AnthropicAdapter(model=args.model, max_tokens=args.max_tokens)


def _run_cases(args: argparse.Namespace) -> tuple[list, list[dict]]:
    cases = load_cases(args.dataset)
    if getattr(args, "case_id", None):
        cases = [case for case in cases if case.case_id == args.case_id]
        if not cases:
            raise SystemExit(f"Unknown case ID: {args.case_id}")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    completed: set[tuple[str, str]] = set()
    if output.exists():
        if args.overwrite:
            output.unlink()
        elif args.resume:
            existing = load_responses(output)
            completed = {(response.case_id, response.model) for response in existing}
        else:
            raise SystemExit(
                f"Output already exists: {output}. Use --resume or --overwrite."
            )

    error_output = Path(args.error_output) if args.error_output else output.with_suffix(".errors.jsonl")
    if args.overwrite and error_output.exists():
        error_output.unlink()

    adapter = _build_adapter(args)
    errors: list[dict] = []
    new_responses = []
    for case in cases:
        if (case.case_id, args.model) in completed:
            console.print(f"Skipping {case.case_id}: already present for {args.model}")
            continue
        console.print(f"Running {case.case_id}: {case.title}")
        last_error: Exception | None = None
        for attempt in range(args.retries + 1):
            try:
                response = adapter.run_case(case)
                append_jsonl(output, response.model_dump(mode="json"))
                new_responses.append(response)
                last_error = None
                break
            except Exception as exc:  # noqa: BLE001 - CLI must preserve partial runs
                last_error = exc
                if attempt < args.retries:
                    console.print(f"  Retry {attempt + 1}/{args.retries} after: {exc}")
                    time.sleep(args.retry_delay)
        if last_error is not None:
            record = {
                "case_id": case.case_id,
                "model": args.model,
                "error_type": type(last_error).__name__,
                "error": str(last_error),
            }
            append_jsonl(error_output, record)
            errors.append(record)
            console.print(f"[red]Failed {case.case_id}:[/red] {last_error}")
            if not args.continue_on_error:
                raise SystemExit(f"Run stopped after failure in {case.case_id}") from last_error

    total = len(existing) + len(new_responses)
    console.print(f"Responses available: [bold]{total}[/bold] in [bold]{output}[/bold]")
    if errors:
        console.print(f"Errors: [bold]{len(errors)}[/bold] in [bold]{error_output}[/bold]")
    return load_responses(output) if output.exists() else [], errors


def cmd_run(args: argparse.Namespace) -> None:
    _run_cases(args)


def _score_rows(dataset: str, responses_path: str):
    cases = {case.case_id: case for case in load_cases(dataset)}
    responses = load_responses(responses_path)
    scores = []
    for response in responses:
        if response.case_id not in cases:
            raise SystemExit(f"Response references unknown case: {response.case_id}")
        scores.append(score_response(cases[response.case_id], response))
    return scores


def _write_scores(scores, output: str | Path) -> None:
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for score in scores:
        row = score.model_dump(mode="json")
        for key, value in list(row.items()):
            if isinstance(value, (list, dict)):
                row[key] = json.dumps(value, ensure_ascii=False)
        rows.append(row)
    if not rows:
        raise SystemExit("No valid responses were available to score")
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def cmd_score(args: argparse.Namespace) -> None:
    scores = _score_rows(args.dataset, args.responses)
    _write_scores(scores, args.output)
    table = Table(title="BioReasonBench automated rubric scores")
    table.add_column("Case")
    table.add_column("Model")
    table.add_column("Score", justify="right")
    table.add_column("Field coverage", justify="right")
    for score in scores:
        table.add_row(
            score.case_id,
            score.model,
            f"{score.total_score:.1f}",
            f"{score.field_concept_coverage:.1f}",
        )
    console.print(table)
    console.print(f"Wrote scores to [bold]{args.output}[/bold]")


def cmd_report(args: argparse.Namespace) -> None:
    cases = load_cases(args.dataset)
    responses = load_responses(args.responses)
    case_map = {case.case_id: case for case in cases}
    scores = [score_response(case_map[r.case_id], r) for r in responses]
    write_report(
        cases=cases,
        responses=responses,
        scores=scores,
        output=args.output,
        metrics_output=args.metrics_output,
        expert_reviews=args.expert_reviews,
    )
    console.print(f"Wrote report to [bold]{args.output}[/bold]")


def cmd_pipeline(args: argparse.Namespace) -> None:
    run_dir = Path(args.output_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    responses_path = run_dir / "responses.jsonl"
    errors_path = run_dir / "errors.jsonl"
    scores_path = run_dir / "scores.csv"
    report_path = run_dir / "report.html"
    metrics_path = run_dir / "metrics.json"

    run_args = argparse.Namespace(
        dataset=args.dataset,
        adapter="anthropic",
        model=args.model,
        max_tokens=args.max_tokens,
        case_id=None,
        output=str(responses_path),
        error_output=str(errors_path),
        resume=True,
        overwrite=args.overwrite,
        retries=args.retries,
        retry_delay=args.retry_delay,
        continue_on_error=True,
    )
    responses, errors = _run_cases(run_args)
    if not responses:
        raise SystemExit("Pipeline produced no valid responses")

    case_map = {case.case_id: case for case in load_cases(args.dataset)}
    scores = [score_response(case_map[r.case_id], r) for r in responses]
    _write_scores(scores, scores_path)
    write_report(
        cases=list(case_map.values()),
        responses=responses,
        scores=scores,
        output=report_path,
        metrics_output=metrics_path,
        expert_reviews=args.expert_reviews,
    )
    console.print("\n[bold]Pipeline complete[/bold]")
    console.print(f"Responses: {responses_path}")
    console.print(f"Scores:    {scores_path}")
    console.print(f"Report:    {report_path}")
    console.print(f"Metrics:   {metrics_path}")
    if errors:
        console.print(f"Errors:    {errors_path}")


def _add_run_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--dataset", default="data/benchmark.jsonl")
    parser.add_argument("--adapter", default="anthropic")
    parser.add_argument("--model", default="claude-sonnet-5")
    parser.add_argument("--max-tokens", type=int, default=1800)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--retry-delay", type=float, default=2.0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="biofigurebench")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate")
    validate.add_argument("--dataset", default="data/benchmark.jsonl")
    validate.set_defaults(func=cmd_validate)

    run = subparsers.add_parser("run", help="Run one case or all cases")
    _add_run_options(run)
    run.add_argument("--case-id")
    run.add_argument("--output", required=True)
    run.add_argument("--error-output")
    run.add_argument("--resume", action="store_true")
    run.add_argument("--overwrite", action="store_true")
    run.add_argument("--continue-on-error", action="store_true")
    run.set_defaults(func=cmd_run)

    score = subparsers.add_parser("score")
    score.add_argument("--dataset", default="data/benchmark.jsonl")
    score.add_argument("--responses", required=True)
    score.add_argument("--output", required=True)
    score.set_defaults(func=cmd_score)

    report = subparsers.add_parser("report")
    report.add_argument("--dataset", default="data/benchmark.jsonl")
    report.add_argument("--responses", required=True)
    report.add_argument("--output", required=True)
    report.add_argument("--metrics-output")
    report.add_argument("--expert-reviews")
    report.set_defaults(func=cmd_report)

    pipeline = subparsers.add_parser("pipeline", help="Run, score, and report all cases")
    _add_run_options(pipeline)
    pipeline.add_argument("--output-dir", required=True)
    pipeline.add_argument("--overwrite", action="store_true")
    pipeline.add_argument("--expert-reviews")
    pipeline.set_defaults(func=cmd_pipeline)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
