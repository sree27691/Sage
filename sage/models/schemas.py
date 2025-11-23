from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class ProductContext(BaseModel):
    product_id: str
    url: str
    pdp_html: str
    images: List[str]
    reviews_html: Optional[str] = None
    source: Literal["web_app", "browser_extension"]
    timestamp: str
    user_question: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    structured_content: Optional[Dict[str, Optional[str]]] = None

class EvidenceUnit(BaseModel):
    evidence_id: str
    product_id: str
    source_type: Literal["pdp", "reddit", "youtube", "vlm_image", "pdf_text"]
    text: str
    aspect_tags: List[str]
    metadata: Dict[str, Any]
    timestamp: str

class AspectSummary(BaseModel):
    name: str
    score_0_10: int
    pros: List[str]
    cons: List[str]
    dealbreakers: List[str]

class TrustSummary(BaseModel):
    product_id: str
    overall_verdict: str
    aspects: List[AspectSummary]
    claims: List[str]
    conflicts: List[str]
    uncertainties: List[str]

class TCSComponents(BaseModel):
    groundedness: float
    accuracy: float
    coverage: float
    conflict_detection: float
    uncertainty: float
    tcs_score: float
    band: Literal["Elite", "Production Safe", "Pilot", "Unsafe"]

class PlannerOutput(BaseModel):
    mode: str
    product_ids: List[str]
    aspects: List[str]
    sources_to_use: List[str]
    retrieval_config: Dict[str, Any]
    notes_for_summarizer: str

class ClaimJudgement(BaseModel):
    claim_text: str
    evidence_ids: List[str]
    judge_label: Literal["Supported", "PartiallySupported", "Unsupported", "Contradicted"]
    reasoning: str

class JudgeOutput(BaseModel):
    claims_judgement: List[ClaimJudgement]
    conflicts: List[str]
    uncertainty_aspects: List[str]
