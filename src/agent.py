import re
from typing import List, Dict, Any, Optional
from src.engine import EnvironmentalScientistEngine
from src.models import ChatbotAnalysisResult

class BiodiversityAgent:
    def __init__(self, engine: Optional[EnvironmentalScientistEngine] = None):
        self.engine = engine or EnvironmentalScientistEngine()
        self.history: List[Dict[str, str]] = []
        self.accumulated_variables: Dict[str, Any] = {}

    def reset(self):
        self.history = []
        self.accumulated_variables = {}

    def update_variables_from_text(self, text: str):
        text_lower = text.lower()
        soc_match = re.search(r"(\d+(?:\.\d+)?)\s*%\s*(?:soc|soil organic carbon|carbon)?", text_lower)
        if soc_match and ("carbon" in text_lower or "soc" in text_lower or "%" in text_lower):
            self.accumulated_variables["soil_organic_carbon"] = f"{soc_match.group(1)}%"

        for r in ["low", "moderate", "high", "erratic", "semi-arid"]:
            if r in text_lower and ("rain" in text_lower or "precipitation" in text_lower or r in ["low", "erratic"]):
                self.accumulated_variables["rainfall"] = r

        for c in ["monoculture wheat", "wheat", "corn", "soybean", "barley", "maize", "paddy", "cotton", "rice"]:
            if c in text_lower:
                self.accumulated_variables["crop"] = c
                break

        for reg in ["semi-arid", "arid", "mediterranean", "temperate", "tropical", "sub-humid"]:
            if reg in text_lower:
                self.accumulated_variables["region"] = reg
                break

        for t in ["conventional tillage", "deep plow", "moldboard", "no-till", "strip-till", "reduced till"]:
            if t in text_lower:
                self.accumulated_variables["tillage"] = t
                break

    def chat(self, user_message: str, structured_override: Optional[Dict[str, Any]] = None) -> ChatbotAnalysisResult:
        if structured_override:
            for k, v in structured_override.items():
                if v:
                    self.accumulated_variables[k] = v

        self.update_variables_from_text(user_message)

        result = self.engine.analyze(
            user_text=user_message,
            structured_vars=self.accumulated_variables,
            conversation_history=self.history
        )

        if result.detected_variables:
            for k, v in result.detected_variables.items():
                if isinstance(v, (str, int, float)) and k not in ["detected_dimensions"]:
                    self.accumulated_variables[k] = v

        if result.is_clarifying_required:
            q_lines = "\n".join([f"- {q}" for q in result.clarifying_questions])
            assistant_reply = f"I need a few baseline metrics to give you a scientifically grounded recommendation:\n{q_lines}"
        else:
            rec_titles = [f"'{r.title}'" for r in result.recommendations]
            assistant_reply = f"{result.synthesis_summary}\nKey Interventions: {', '.join(rec_titles)}."

        self.history.append({
            "user": user_message,
            "assistant": assistant_reply
        })

        return result
