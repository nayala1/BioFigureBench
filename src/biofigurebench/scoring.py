from __future__ import annotations

import re
from collections.abc import Iterable

from .models import BenchmarkCase, ModelResponse, ScoreBreakdown

NEGATIONS = {"no", "not", "never", "cannot", "cant", "doesnt", "isnt", "without"}


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _field_text(response: ModelResponse, field: str) -> str:
    value = getattr(response.answer, field)
    if isinstance(value, list):
        return _normalize(" ".join(value))
    return _normalize(value)


def _assertion_text(response: ModelResponse) -> str:
    answer = response.answer
    return _normalize(
        " ".join(
            [
                answer.experiment,
                *answer.observations,
                *answer.controls_and_statistics,
                answer.supported_conclusion,
                answer.follow_up,
            ]
        )
    )


def _concept_present(text: str, concept: str) -> bool:
    normalized = _normalize(concept)
    if not normalized:
        return False
    if normalized in text:
        return True
    tokens = [token for token in normalized.split() if len(token) > 3]
    if not tokens:
        return False
    required = max(1, int(len(tokens) * 0.75 + 0.5))
    return sum(token in text for token in tokens) >= required


def _asserted_phrase_present(text: str, phrase: str) -> bool:
    """Match an explicit contradiction/overclaim while ignoring local negation."""
    phrase_tokens = _normalize(phrase).split()
    text_tokens = text.split()
    if not phrase_tokens or len(phrase_tokens) > len(text_tokens):
        return False

    # Allow a few intervening words, but require every phrase token. This is
    # intentionally conservative so automated penalties do not dominate the MVP.
    window = len(phrase_tokens) + 4
    for start in range(0, len(text_tokens)):
        candidate = text_tokens[start : start + window]
        if not all(token in candidate for token in phrase_tokens):
            continue
        prior = text_tokens[max(0, start - 4) : start]
        if any(token in NEGATIONS for token in prior + candidate):
            continue
        return True
    return False


def _nonempty(values: Iterable[str]) -> bool:
    return any(value.strip() for value in values)


def score_response(case: BenchmarkCase, response: ModelResponse) -> ScoreBreakdown:
    matched_by_field: dict[str, list[str]] = {}
    missing_by_field: dict[str, list[str]] = {}
    field_scores: dict[str, float] = {}
    total_concepts = 0
    total_matched = 0

    for field, concepts in case.scoring.field_concepts.items():
        text = _field_text(response, field)
        matched = [concept for concept in concepts if _concept_present(text, concept)]
        missing = [concept for concept in concepts if concept not in matched]
        matched_by_field[field] = matched
        missing_by_field[field] = missing
        total_concepts += len(concepts)
        total_matched += len(matched)
        field_scores[field] = round(100 * len(matched) / len(concepts), 1) if concepts else 100.0

    concept_score = total_matched / total_concepts if total_concepts else 0.0
    assertion_text = _assertion_text(response)

    triggered_prohibited = [
        claim
        for claim in case.scoring.prohibited_claims
        if _asserted_phrase_present(assertion_text, claim)
    ]
    triggered_contradictions = [
        claim
        for claim in case.scoring.contradictory_claims
        if _asserted_phrase_present(assertion_text, claim)
    ]
    total_safety_checks = len(case.scoring.prohibited_claims) + len(case.scoring.contradictory_claims)
    total_triggers = len(triggered_prohibited) + len(triggered_contradictions)
    claim_safety = (
        1.0
        if total_safety_checks == 0
        else max(0.0, 1.0 - total_triggers / total_safety_checks)
    )

    answer = response.answer
    completeness_checks = [
        bool(answer.experiment.strip()),
        _nonempty(answer.observations),
        _nonempty(answer.controls_and_statistics),
        bool(answer.supported_conclusion.strip()),
        bool(answer.unsupported_claim.strip()),
        bool(answer.follow_up.strip()),
    ]
    completeness = sum(completeness_checks) / len(completeness_checks)

    # This is an automated rubric proxy, not an expert biological-accuracy score.
    total = 100 * (0.65 * concept_score + 0.25 * claim_safety + 0.10 * completeness)
    triggered_tags = case.scoring.error_tags if total_triggers else []

    return ScoreBreakdown(
        case_id=case.case_id,
        model=response.model,
        field_concept_coverage=round(100 * concept_score, 1),
        claim_safety=round(100 * claim_safety, 1),
        response_completeness=round(100 * completeness, 1),
        total_score=round(total, 1),
        field_scores=field_scores,
        matched_field_concepts=matched_by_field,
        missing_field_concepts=missing_by_field,
        triggered_prohibited_claims=triggered_prohibited,
        triggered_contradictions=triggered_contradictions,
        triggered_error_tags=triggered_tags,
    )
