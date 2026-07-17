from pathlib import Path

from biofigurebench.dataset import load_cases
from biofigurebench.models import ModelAnswer, ModelResponse
from biofigurebench.reporting import write_report
from biofigurebench.scoring import score_response


def test_report_contains_all_cases(tmp_path: Path) -> None:
    dataset = Path(__file__).parents[1] / "data" / "benchmark.jsonl"
    cases = load_cases(dataset)
    responses = []
    scores = []
    for case in cases:
        response = ModelResponse(
            case_id=case.case_id,
            model="reference",
            answer=ModelAnswer(**case.reference.model_dump()),
            latency_seconds=1.0,
        )
        responses.append(response)
        scores.append(score_response(case, response))
    output = tmp_path / "report.html"
    metrics = tmp_path / "metrics.json"
    write_report(
        cases=cases,
        responses=responses,
        scores=scores,
        output=output,
        metrics_output=metrics,
    )
    text = output.read_text()
    assert "5/5" in text
    for case in cases:
        assert case.case_id in text
    assert metrics.exists()


def test_report_accepts_publication_expert_score_column(tmp_path: Path) -> None:
    dataset = Path(__file__).parents[1] / "data" / "benchmark.jsonl"
    cases = load_cases(dataset)
    responses = []
    scores = []
    review_rows = ["case_id,model,expert_score"]
    for case in cases:
        response = ModelResponse(
            case_id=case.case_id,
            model="reference",
            answer=ModelAnswer(**case.reference.model_dump()),
            latency_seconds=1.0,
        )
        responses.append(response)
        scores.append(score_response(case, response))
        review_rows.append(f"{case.case_id},reference,91.0")

    expert_reviews = tmp_path / "expert_review_scores.csv"
    expert_reviews.write_text("\n".join(review_rows) + "\n", encoding="utf-8")
    output = tmp_path / "report.html"
    write_report(
        cases=cases,
        responses=responses,
        scores=scores,
        output=output,
        expert_reviews=expert_reviews,
    )

    text = output.read_text()
    assert "91.0" in text
