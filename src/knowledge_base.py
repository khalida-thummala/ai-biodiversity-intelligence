import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

class ScientificKnowledgeBase:
    def __init__(self, corpus_path: Optional[str] = None):
        if corpus_path is None:
            base_dir = Path(__file__).parent.parent
            corpus_path = base_dir / "data" / "scientific_corpus.json"
        
        self.corpus_path = Path(corpus_path)
        self.records: List[Dict[str, Any]] = []
        self._load_corpus()

    def _load_corpus(self):
        if not self.corpus_path.exists():
            raise FileNotFoundError(f"Scientific corpus not found at {self.corpus_path}")
        with open(self.corpus_path, "r", encoding="utf-8") as f:
            self.records = json.load(f)

    def get_all_records(self) -> List[Dict[str, Any]]:
        return self.records

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Hybrid retrieval scoring records based on term match, domain relevance,
        climate zone alignment, and degradation drivers.
        """
        if not self.records:
            return []

        query_lower = query.lower()
        query_terms = set(query_lower.replace(",", " ").replace(".", " ").replace("%", "").split())

        scored_records = []
        for record in self.records:
            score = 0.0
            searchable_text = " ".join([
                record.get("title", ""),
                record.get("domain", ""),
                " ".join(record.get("subdomains", [])),
                " ".join(record.get("climate_zones", [])),
                " ".join(record.get("land_use", [])),
                record.get("intervention", ""),
                record.get("scientific_mechanisms", ""),
                record.get("multi_metric_chain", ""),
                str(record.get("baseline_conditions", {}))
            ]).lower()

            for term in query_terms:
                if len(term) <= 2:
                    continue
                if term in searchable_text:
                    score += 1.5
                    # Higher weight if found in domain or land_use or baseline
                    if term in " ".join(record.get("land_use", [])).lower():
                        score += 3.0
                    if term in " ".join(record.get("climate_zones", [])).lower():
                        score += 2.5
                    if term in record.get("domain", "").lower():
                        score += 2.0

            # Boost specific key concept combinations
            if ("carbon" in query_lower or "soc" in query_lower) and "carbon" in searchable_text:
                score += 3.5
            if ("semi-arid" in query_lower or "arid" in query_lower) and ("semi-arid" in searchable_text or "arid" in searchable_text):
                score += 4.0
            if ("wheat" in query_lower or "cereal" in query_lower) and ("wheat" in searchable_text or "cereal" in searchable_text):
                score += 4.0
            if ("rain" in query_lower or "water" in query_lower or "drought" in query_lower) and ("water" in searchable_text or "rainfall" in searchable_text):
                score += 2.5
            if ("pollinator" in query_lower or "bee" in query_lower) and "pollinator" in searchable_text:
                score += 3.5
            if ("tillage" in query_lower or "plow" in query_lower) and "tillage" in searchable_text:
                score += 3.0
            if ("agroforestry" in query_lower or "tree" in query_lower) and "agroforestry" in searchable_text:
                score += 3.5

            scored_records.append((score, record))

        scored_records.sort(key=lambda x: x[0], reverse=True)
        top_records = [rec for score, rec in scored_records if score > 0][:top_k]
        
        # Fallback if no specific keyword matched: return top default diverse records
        if not top_records:
            top_records = self.records[:top_k]

        return top_records

    def format_retrieved_context(self, records: List[Dict[str, Any]]) -> str:
        """Formats retrieved records into a structured context string for scientific reasoning."""
        chunks = []
        for idx, r in enumerate(records, 1):
            impacts = "; ".join([f"{k}: {v}" for k, v in r.get("quantitative_impacts", {}).items()])
            citations = "; ".join(r.get("citations", []))
            chunk = (
                f"--- SCIENTIFIC BENCHMARK [{idx}] ---\n"
                f"ID: {r.get('id')}\n"
                f"Title: {r.get('title')}\n"
                f"Domain: {r.get('domain')} ({r.get('subdomains', [])})\n"
                f"Climate Zones: {r.get('climate_zones', [])}\n"
                f"Land Use Match: {r.get('land_use', [])}\n"
                f"Intervention: {r.get('intervention')}\n"
                f"Scientific Mechanisms: {r.get('scientific_mechanisms')}\n"
                f"Quantitative Impacts: {impacts}\n"
                f"Multi-Metric Causal Chain: {r.get('multi_metric_chain')}\n"
                f"Time Horizon: {r.get('time_horizon')}\n"
                f"Confidence: {r.get('confidence_level')}\n"
                f"Credible Citations: {citations}\n"
            )
            chunks.append(chunk)
        return "\n".join(chunks)

if __name__ == "__main__":
    kb = ScientificKnowledgeBase()
    print(f"Knowledge base loaded with {len(kb.records)} records.")
    results = kb.retrieve("soil organic carbon 0.3% low rainfall semi-arid monoculture wheat")
    print(f"Top {len(results)} matches:")
    for r in results:
        print(f" - [{r['id']}] {r['title']}")
