from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, model_validator

AnswerField = Literal[
    "experiment",
    "observations",
    "controls_and_statistics",
    "supported_conclusion",
    "unsupported_claim",
    "follow_up",
]


class SourceMetadata(BaseModel):
    article_title: str
    citation: str
    doi: str
    figure_id: str
    article_url: HttpUrl
    figure_page_url: HttpUrl
    image_url: HttpUrl
    license: str
    attribution: str


class ReferenceAnswer(BaseModel):
    experiment: str
    observations: list[str]
    controls_and_statistics: list[str]
    supported_conclusion: str
    unsupported_claim: str
    follow_up: str


class ScoringSpec(BaseModel):
    field_concepts: dict[AnswerField, list[str]]
    prohibited_claims: list[str] = Field(default_factory=list)
    contradictory_claims: list[str] = Field(default_factory=list)
    error_tags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_field_concepts(self) -> "ScoringSpec":
        if not any(self.field_concepts.values()):
            raise ValueError("At least one field-specific scoring concept is required")
        return self


class BenchmarkCase(BaseModel):
    case_id: str = Field(pattern=r"^BFB-\d{3}$")
    title: str
    domain: str
    figure_type: list[str]
    difficulty: Literal["introductory", "intermediate", "advanced"]
    context: str
    legend_excerpt: str
    prompt: str
    source: SourceMetadata
    reference: ReferenceAnswer
    scoring: ScoringSpec

    @model_validator(mode="after")
    def validate_claim_separation(self) -> "BenchmarkCase":
        if self.reference.supported_conclusion.strip() == self.reference.unsupported_claim.strip():
            raise ValueError("Supported and unsupported claims must differ")
        return self


class ModelAnswer(BaseModel):
    experiment: str
    observations: list[str]
    controls_and_statistics: list[str]
    supported_conclusion: str
    unsupported_claim: str
    follow_up: str


class ModelResponse(BaseModel):
    case_id: str
    model: str
    answer: ModelAnswer
    raw_text: str | None = None
    latency_seconds: float | None = None


class ScoreBreakdown(BaseModel):
    case_id: str
    model: str
    field_concept_coverage: float
    claim_safety: float
    response_completeness: float
    total_score: float
    field_scores: dict[str, float]
    matched_field_concepts: dict[str, list[str]]
    missing_field_concepts: dict[str, list[str]]
    triggered_prohibited_claims: list[str]
    triggered_contradictions: list[str]
    triggered_error_tags: list[str]
