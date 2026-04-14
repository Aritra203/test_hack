from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
SeverityLabel = Literal["cyberbullying", "threat", "hate_speech", "sexual_harassment"]


class ConversationMessage(BaseModel):
    sender: str = Field(..., min_length=1, max_length=120)
    message: str = Field(..., min_length=1, max_length=5000)
    timestamp: datetime | None = None


class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    previous_messages: list[ConversationMessage] = Field(default_factory=list)
    language_hint: str | None = Field(default=None, max_length=32)
    subject_is_minor: bool = False


class ExplainableSpan(BaseModel):
    term: str
    reason: str


class LabelScore(BaseModel):
    label: SeverityLabel
    score: float = Field(..., ge=0, le=1)


class LegalSection(BaseModel):
    section: str
    law: str
    rationale: str


class AnalysisResultPayload(BaseModel):
    toxicity_score: float = Field(..., ge=0, le=1)
    risk_level: RiskLevel
    labels: list[LabelScore]
    explainable_spans: list[ExplainableSpan]
    normalized_text: str
    detected_language: str
    grooming_signals: list[str]
    context_summary: str
    escalation_detected: bool
    legal_sections: list[LegalSection]


class TextAnalysisResponse(BaseModel):
    analysis_id: str
    analyzed_text: str
    result: AnalysisResultPayload
    created_at: datetime


class ImageAnalysisResponse(BaseModel):
    evidence_id: str
    extracted_text: str
    cloudinary_url: HttpUrl
    cloudinary_public_id: str
    result: AnalysisResultPayload
    created_at: datetime


class FIRGenerationRequest(BaseModel):
    complainant_name: str = Field(..., min_length=2, max_length=160)
    complainant_contact: str = Field(..., min_length=5, max_length=64)
    incident_description: str = Field(..., min_length=10, max_length=6000)
    location: str = Field(..., min_length=2, max_length=200)
    incident_datetime: datetime
    accused_details: str | None = Field(default=None, max_length=1000)
    additional_notes: str | None = Field(default=None, max_length=2000)
    previous_messages: list[ConversationMessage] = Field(default_factory=list)
    language_hint: str | None = Field(default=None, max_length=32)
    subject_is_minor: bool = False
    evidence_urls: list[HttpUrl] = Field(default_factory=list)


class FIRGenerationResponse(BaseModel):
    fir_id: str
    filename: str
    job_id: str
    status: Literal["queued", "completed", "failed"]


class FIRJobStatusResponse(BaseModel):
    job_id: str
    status: Literal["queued", "completed", "failed"]
    fir_id: str | None = None
    filename: str | None = None
    error: str | None = None


class AnalyticsResponse(BaseModel):
    total_analyses: int
    by_risk: dict[str, int]
    by_label: dict[str, int]
    recent_incidents: int

