import json
from typing import Dict, Any, List
from sage.models.schemas import TrustSummary, EvidenceUnit
from sage.utils.llm_client import LLMClient

SUMMARIZER_SYSTEM_PROMPT = """You are the Summarizer Agent for Sage.
Your job is to:
- Produce a structured Trust Summary grounded ONLY in retrieved evidence.
- Write claims with explicit evidence_ids.
- Provide aspect-wise summaries and dealbreakers.
- List conflicts (e.g., specs vs. user experience) and uncertainties (missing info).
- If evidence is thin for an aspect, mark it as an uncertainty.

CRITICAL RULES:
- NO SPECULATION OR HALLUCINATION - Only use information explicitly present in the evidence.
- PRODUCT-SPECIFIC ANALYSIS - Analyze ONLY the actual product type (e.g., refrigerator, headphones, laptop).
- DO NOT use generic aspects - Identify aspects relevant to THIS specific product category.
- If you don't have evidence for an aspect, DO NOT include it in the output.
- Always cite evidence_ids for every claim.
- Prefer consensus; highlight outliers.

Examples of CORRECT aspect selection:
- Refrigerator: Cooling Performance, Energy Efficiency, Storage Capacity, Noise Level, Build Quality
- Headphones: Sound Quality, Battery Life, Comfort, ANC, Connectivity
- Laptop: Performance, Battery Life, Display Quality, Build Quality, Keyboard

DO NOT mix aspects from different product categories!

Output JSON:
{
"product_id": "...",
"overall_verdict": "...",
"aspects": [
    {
        "name": "Aspect Name (e.g. Cooling Performance for refrigerator)",
        "score_0_10": 8,
        "pros": ["..."],
        "cons": ["..."],
        "dealbreakers": ["..."]
    }
],
"claims": ["..."],
"conflicts": ["..."],
"uncertainties": ["..."]
}"""

class SummarizerAgent:
    def __init__(self):
        self.client = LLMClient()
        self.agent_name = "summarizer_trust"

    def summarize(self, product_id: str, evidence: List[Dict[str, Any]]) -> TrustSummary:
        print(f"[SUMMARIZER] Product ID: {product_id}")
        print(f"[SUMMARIZER] Evidence count: {len(evidence)}")
        print(f"[SUMMARIZER] Evidence preview: {evidence[:2] if evidence else 'No evidence'}")
        
        user_content = f"""
        Product ID: {product_id}
        Evidence Bundle:
        {json.dumps(evidence, indent=2)}
        """
        
        print(f"[SUMMARIZER] Calling LLM with {len(user_content)} chars of context...")
        response_str = self.client.generate_response(
            system_prompt=SUMMARIZER_SYSTEM_PROMPT,
            user_content=user_content,
            agent_name=self.agent_name,
            response_format=TrustSummary,
            temperature=0.0
        )
        
        print(f"[SUMMARIZER] LLM response length: {len(response_str)} chars")
        print(f"[SUMMARIZER] Response preview: {response_str[:500]}...")
        
        try:
            data = json.loads(response_str)
            # Ensure the data matches TrustSummary schema
            summary = TrustSummary(**data)
            print(f"[SUMMARIZER] Created TrustSummary with {len(summary.aspects)} aspects")
            for aspect in summary.aspects:
                print(f"[SUMMARIZER]   - {aspect.name}: {aspect.score_0_10}/10")
            return summary
        except json.JSONDecodeError:
            raise ValueError("Failed to parse Summarizer response")
