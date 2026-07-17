from pathlib import Path

from biofigurebench.dataset import load_cases
from biofigurebench.models import ModelAnswer, ModelResponse
from biofigurebench.scoring import score_response


def _reference_response(case):
    return ModelResponse(
        case_id=case.case_id,
        model="reference",
        answer=ModelAnswer(
            experiment=case.reference.experiment,
            observations=case.reference.observations,
            controls_and_statistics=case.reference.controls_and_statistics,
            supported_conclusion=case.reference.supported_conclusion,
            unsupported_claim=case.reference.unsupported_claim,
            follow_up=case.reference.follow_up,
        ),
    )


def test_reference_answers_score_well_for_all_cases() -> None:
    path = Path(__file__).parents[1] / "data" / "benchmark.jsonl"
    for case in load_cases(path):
        score = score_response(case, _reference_response(case))
        assert score.total_score >= 85, (case.case_id, score)
        assert not score.triggered_prohibited_claims
        assert not score.triggered_contradictions


def test_field_scoping_prevents_concept_credit_in_wrong_field() -> None:
    path = Path(__file__).parents[1] / "data" / "benchmark.jsonl"
    case = {case.case_id: case for case in load_cases(path)}["BFB-001"]
    response = _reference_response(case)
    response.answer.observations = ["Internal structures are visible."]
    response.answer.follow_up += " Label-free 2D and 3D refractive-index images."
    score = score_response(case, response)
    assert "high-contrast 2D and 3D representations" in score.missing_field_concepts[
        "observations"
    ]


def test_bfb002_visual_contradiction_is_penalized() -> None:
    path = Path(__file__).parents[1] / "data" / "benchmark.jsonl"
    case = {case.case_id: case for case in load_cases(path)}["BFB-002"]
    response = _reference_response(case)
    response.answer.observations.append("Panel E shows varicosities or branch points.")
    score = score_response(case, response)
    assert score.triggered_contradictions
    assert score.claim_safety < 100
