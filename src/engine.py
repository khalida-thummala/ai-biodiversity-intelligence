import os
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.knowledge_base import ScientificKnowledgeBase
from src.models import (
    EnvironmentalContext,
    SingleRecommendation,
    ChatbotAnalysisResult
)

load_dotenv()

class EnvironmentalScientistEngine:
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-3.6-flash"):
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            try:
                import streamlit as st
                if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                    api_key = st.secrets["GEMINI_API_KEY"]
            except Exception:
                pass
        self.api_key = api_key
        try:
            self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        except Exception as e:
            print("Gemini client initialization notice:", e)
            self.client = None
        self.model_name = model_name
        self.kb = ScientificKnowledgeBase()

    def infer_spatial_context(self, lat: float, lon: float) -> Dict[str, str]:
        abs_lat = abs(lat)
        if abs_lat < 15:
            zone = "Tropical (High Seasonal / Monsoonal Rainfall 800-2000mm)"
        elif 15 <= abs_lat <= 35:
            zone = "Subtropical / Semi-Arid to Arid (Low / Erratic Rainfall 200-500mm)"
        elif 35 < abs_lat <= 55:
            zone = "Temperate (Moderate Rainfall 500-1000mm)"
        else:
            zone = "Boreal / Sub-polar (Low Evapotranspiration)"
        return {
            "estimated_biome": zone,
            "coordinates": f"{lat:.4f}, {lon:.4f}"
        }

    def assess_variable_sufficiency(self, variables: Dict[str, Any], query_text: str = "") -> Tuple[bool, List[str], List[str]]:
        detected = []
        missing = []
        q_lower = query_text.lower()
        
        has_soil = bool(variables.get("soil_organic_carbon") or variables.get("soil_ph") or any(k in q_lower for k in ["soil", "carbon", "soc", "ph"]))
        if has_soil:
            detected.append("soil_health")
        else:
            missing.append("Soil Organic Carbon (SOC %) or Soil pH baseline")

        has_climate = bool(variables.get("rainfall") or variables.get("region") or any(k in q_lower for k in ["rain", "semi-arid", "arid", "drought", "water", "precipitation", "dryland", "moisture"]))
        if has_climate:
            detected.append("climate_water")
        else:
            missing.append("Rainfall pattern or climate region (e.g., semi-arid, low rainfall)")

        has_land_use = bool(variables.get("crop") or variables.get("tillage") or any(k in q_lower for k in ["crop", "wheat", "monoculture", "tillage", "plow", "farmland", "pasture", "orchard", "land use", "cover crop"]))
        if has_land_use:
            detected.append("land_use")
        else:
            missing.append("Current land use, cropping system (e.g., monoculture wheat), or tillage practices")

        if any(k in q_lower for k in ["biodiversity", "pollinator", "species", "earthworm", "wildlife", "invertebrate"]):
            detected.append("biodiversity_status")

        is_sufficient = len(detected) >= 3
        return is_sufficient, detected, missing

    def build_system_prompt(self) -> str:
        return """You are the Lead AI Environmental Scientist at Darukaa.Earth.
Your goal is to evaluate land ecosystems and generate actionable, scientifically grounded biodiversity restoration strategies.

CORE EVALUATION CRITERIA:
1. DEPTH OF REASONING: Every recommendation must combine at least 3 environmental variables together (e.g., Soil Organic Carbon <-> Water Infiltration <-> Species Survival/Trophic Diversity). Avoid shallow or obvious advice.
2. SCIENTIFIC GROUNDING: Support every recommendation with biochemical and ecological mechanisms. Provide measurable quantitative improvement estimates and cite credible bodies (FAO, IPCC, IPBES, CGIAR, Lal et al.).
3. CONVERSATIONAL INTELLIGENCE: If the user query is underspecified (less than 3 environmental variables provided, e.g., "Biodiversity is declining on my land"), DO NOT jump to solutions. Set "is_clarifying_required": true and ask targeted scientific clarifying questions for the missing parameters (soil organic carbon %, rainfall pattern, land use/crop).

OUTPUT FORMAT (Strict JSON):
{
  "is_clarifying_required": boolean,
  "clarifying_questions": ["Question 1", "Question 2"],
  "detected_variables": {"variable_name": "value"},
  "missing_critical_variables": ["Missing item 1"],
  "synthesis_summary": "Scientific diagnosis of limiting factors and ecosystem status",
  "recommendations": [
    {
      "title": "Intervention Name",
      "recommendation": "Specific, concrete action steps",
      "scientific_reasoning": "Ecological/biochemical mechanism explaining why it works",
      "impacted_metrics": ["Soil Organic Carbon: +15% to +25% over 2-3 years", "Water Infiltration: +30%"],
      "multi_metric_chain": "Causal linkage: Soil Carbon -> Water Retention -> Belowground Biota & Pollinator Resilience",
      "citations": ["FAO (2020) Recarbonizing Global Soils", "IPCC (2019) Land Degradation"],
      "time_horizon": "short / medium / long term",
      "confidence_level": "High / Moderate / Conditional"
    }
  ]
}"""

    def analyze(self, user_text: str, structured_vars: Optional[Dict[str, Any]] = None, conversation_history: Optional[List[Dict[str, str]]] = None) -> ChatbotAnalysisResult:
        structured_vars = structured_vars or {}
        conversation_history = conversation_history or []
        
        full_text_context = user_text
        for turn in conversation_history:
            full_text_context += f"\nUser: {turn.get('user', '')}\nAssistant: {turn.get('assistant', '')}"
        
        is_sufficient, detected, missing = self.assess_variable_sufficiency(structured_vars, full_text_context)
        combined_query = f"{user_text} {json.dumps(structured_vars)}"
        retrieved_records = self.kb.retrieve(combined_query, top_k=3)
        retrieved_context_str = self.kb.format_retrieved_context(retrieved_records)

        spatial_bonus_info = ""
        if "latitude" in structured_vars and "longitude" in structured_vars:
            try:
                lat = float(structured_vars["latitude"])
                lon = float(structured_vars["longitude"])
                spatial = self.infer_spatial_context(lat, lon)
                spatial_bonus_info = f"\nSpatial/Biome Context: {json.dumps(spatial)}"
            except Exception:
                pass

        user_prompt = f"""EVALUATION REQUEST:
Current User Query: {user_text}
Structured Input Variables: {json.dumps(structured_vars, indent=2)}
Sufficiency Pre-Assessment: Detected={detected}, Missing={missing}
Conversation History: {json.dumps(conversation_history, indent=2)}{spatial_bonus_info}

RETRIEVED SCIENTIFIC KNOWLEDGE BASE EVIDENCE (Use these studies and citations):
{retrieved_context_str}

INSTRUCTIONS:
1. If input is incomplete (e.g., user says 'Biodiversity is declining on my land' without sufficient metrics), set 'is_clarifying_required': true and formulate 2-3 focused clarifying questions.
2. If input has sufficient variables (e.g., Soil Organic Carbon: 0.3%, Rainfall: low, Crop: monoculture wheat, Region: semi-arid), synthesize deep, multi-metric recommendations linking Soil <-> Water <-> Biodiversity. Include measurable estimates and explicit citations.
Return ONLY valid JSON.
"""
        if not self.client:
            return self._rule_based_fallback(user_text, structured_vars, retrieved_records, is_sufficient, detected, missing)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.build_system_prompt(),
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            elif raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            parsed = json.loads(raw_text.strip())

            recs = []
            for r in parsed.get("recommendations", []):
                recs.append(SingleRecommendation(
                    title=r.get("title", "Ecological Restoration"),
                    recommendation=r.get("recommendation", ""),
                    scientific_reasoning=r.get("scientific_reasoning", ""),
                    impacted_metrics=r.get("impacted_metrics", []),
                    multi_metric_chain=r.get("multi_metric_chain", ""),
                    citations=r.get("citations", []),
                    time_horizon=r.get("time_horizon", "medium-term"),
                    confidence_level=r.get("confidence_level", "High")
                ))

            return ChatbotAnalysisResult(
                is_clarifying_required=parsed.get("is_clarifying_required", False),
                clarifying_questions=parsed.get("clarifying_questions", []),
                detected_variables=parsed.get("detected_variables", {}),
                missing_critical_variables=parsed.get("missing_critical_variables", []),
                synthesis_summary=parsed.get("synthesis_summary", ""),
                recommendations=recs,
                retrieved_sources=retrieved_records
            )
        except Exception as e:
            print(f"Engine LLM warning: {e}")
            return self._rule_based_fallback(user_text, structured_vars, retrieved_records, is_sufficient, detected, missing)

    def _rule_based_fallback(self, user_text: str, structured_vars: Dict[str, Any], retrieved_records: List[Dict[str, Any]], is_sufficient: bool, detected: List[str], missing: List[str]) -> ChatbotAnalysisResult:
        if not is_sufficient:
            return ChatbotAnalysisResult(
                is_clarifying_required=True,
                clarifying_questions=[f"Can you provide your {m}?" for m in missing],
                detected_variables={"detected_dimensions": detected},
                missing_critical_variables=missing,
                synthesis_summary="Insufficient baseline variables to formulate an evidence-backed ecological recommendation.",
                recommendations=[],
                retrieved_sources=retrieved_records
            )

        recs = []
        for r in retrieved_records:
            impacts = [f"{k.replace('_', ' ').title()}: {v}" for k, v in r.get("quantitative_impacts", {}).items()]
            recs.append(SingleRecommendation(
                title=r.get("title", ""),
                recommendation=r.get("intervention", ""),
                scientific_reasoning=r.get("scientific_mechanisms", ""),
                impacted_metrics=impacts,
                multi_metric_chain=r.get("multi_metric_chain", ""),
                citations=r.get("citations", []),
                time_horizon=r.get("time_horizon", "medium-term"),
                confidence_level=r.get("confidence_level", "High")
            ))

        return ChatbotAnalysisResult(
            is_clarifying_required=False,
            clarifying_questions=[],
            detected_variables=structured_vars,
            missing_critical_variables=[],
            synthesis_summary=f"Multi-metric scientific synthesis across {len(detected)} critical environmental dimensions.",
            recommendations=recs,
            retrieved_sources=retrieved_records
        )
