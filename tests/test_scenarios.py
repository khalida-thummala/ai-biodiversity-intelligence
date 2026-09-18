import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.knowledge_base import ScientificKnowledgeBase
from src.engine import EnvironmentalScientistEngine
from src.agent import BiodiversityAgent

def test_knowledge_base_retrieval():
    kb = ScientificKnowledgeBase()
    assert len(kb.records) >= 8
    
    # Query for semi-arid monoculture wheat
    results = kb.retrieve("soil organic carbon 0.3% low rainfall semi-arid monoculture wheat", top_k=3)
    assert len(results) == 3
    retrieved_ids = [r["id"] for r in results]
    assert "FAO-SOIL-001" in retrieved_ids or "IPCC-AGRO-002" in retrieved_ids

def test_incomplete_input_clarification():
    engine = EnvironmentalScientistEngine()
    result = engine.analyze("Biodiversity is declining on my land")
    assert result.is_clarifying_required is True
    assert len(result.clarifying_questions) >= 2
    assert len(result.recommendations) == 0

def test_complete_multi_metric_recommendation():
    engine = EnvironmentalScientistEngine()
    structured_vars = {
        "soil_organic_carbon": "0.3%",
        "rainfall": "low",
        "crop": "monoculture wheat",
        "region": "semi-arid"
    }
    result = engine.analyze(
        user_text="Provide biodiversity interventions for this farm.",
        structured_vars=structured_vars
    )
    assert result.is_clarifying_required is False
    assert len(result.recommendations) >= 1
    rec = result.recommendations[0]
    assert len(rec.citations) >= 1
    assert len(rec.impacted_metrics) >= 1
    assert rec.multi_metric_chain != ""

def test_multi_turn_conversational_memory():
    agent = BiodiversityAgent()
    # Turn 1: Incomplete query
    res1 = agent.chat("Biodiversity is declining on my land")
    assert res1.is_clarifying_required is True
    assert len(agent.history) == 1

    # Turn 2: Provide missing variables
    res2 = agent.chat("My soil organic carbon is 0.3%, rainfall is low, and I grow monoculture wheat in a semi-arid zone.")
    assert res2.is_clarifying_required is False
    assert len(res2.recommendations) >= 1
    assert len(agent.history) == 2

if __name__ == "__main__":
    test_knowledge_base_retrieval()
    print("test_knowledge_base_retrieval PASSED")
    test_incomplete_input_clarification()
    print("test_incomplete_input_clarification PASSED")
    test_complete_multi_metric_recommendation()
    print("test_complete_multi_metric_recommendation PASSED")
    test_multi_turn_conversational_memory()
    print("test_multi_turn_conversational_memory PASSED")
    print("ALL TESTS PASSED SUCCESSFULLY!")
