from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class EnvironmentalContext(BaseModel):
    soil_organic_carbon: Optional[str] = Field(None, description='Soil organic carbon percentage e.g. 0.3%')
    soil_ph: Optional[str] = Field(None, description='Soil pH level e.g. 5.5, 7.2')
    rainfall: Optional[str] = Field(None, description='Rainfall pattern e.g. low, 350mm/yr, semi-arid')
    crop: Optional[str] = Field(None, description='Current cropping system e.g. monoculture wheat, soy')
    region: Optional[str] = Field(None, description='Geographical region or biome e.g. semi-arid, Mediterranean')
    tillage: Optional[str] = Field(None, description='Tillage intensity e.g. conventional moldboard, no-till')
    coordinates: Optional[Dict[str, float]] = Field(None, description='Optional lat/lon coordinates')
    additional_notes: Optional[str] = Field(None, description='Free text background notes')

class SingleRecommendation(BaseModel):
    title: str = Field(..., description='Intervention title')
    recommendation: str = Field(..., description='What to do in concrete terms')
    scientific_reasoning: str = Field(..., description='Why it works at biochemical/ecological level')
    impacted_metrics: List[str] = Field(..., description='Specific metrics improved with estimates')
    multi_metric_chain: str = Field(..., description='Causal linkage across >=3 variables e.g. Soil <-> Water <-> Biodiversity')
    citations: List[str] = Field(..., description='Credible sources e.g. FAO, IPCC, peer-reviewed')
    time_horizon: str = Field(..., description='short / medium / long term')
    confidence_level: str = Field(..., description='High / Moderate / Conditional')

class ChatbotAnalysisResult(BaseModel):
    is_clarifying_required: bool = Field(..., description='True if input is underspecified (<3 variables)')
    clarifying_questions: List[str] = Field(default_factory=list, description='Targeted questions to obtain missing variables')
    detected_variables: Dict[str, Any] = Field(default_factory=dict, description='Variables extracted from input and memory')
    missing_critical_variables: List[str] = Field(default_factory=list, description='Crucial parameters not yet known')
    synthesis_summary: str = Field('', description='High-level scientific diagnosis')
    recommendations: List[SingleRecommendation] = Field(default_factory=list, description='List of evidence-backed recommendations')
    retrieved_sources: List[Dict[str, Any]] = Field(default_factory=list, description='RAG evidence records used')
