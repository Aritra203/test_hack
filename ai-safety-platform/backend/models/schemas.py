from pydantic import BaseModel, Field


class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)


class TextAnalysisResponse(BaseModel):
    analysis_id: str
    analyzed_text: str
    toxicity_score: float
    risk_label: str


class ImageAnalysisResponse(BaseModel):
    evidence_id: str
    extracted_text: str
    toxicity_score: float
    risk_label: str
    cloudinary_url: str
    cloudinary_public_id: str


class FIRGenerationResponse(BaseModel):
    fir_id: str
    filename: str
    download_url: str


class ErrorResponse(BaseModel):
    detail: str
