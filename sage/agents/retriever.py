import json
from typing import List, Dict, Any
from sage.models.schemas import ProductContext, PlannerOutput, EvidenceUnit
from sage.utils.llm_client import LLMClient
from sage.utils.vector_db import VectorDBClient

RETRIEVER_SYSTEM_PROMPT = """You are the Retriever Agent for Sage.
Your job is to:
- Build semantic queries based on question, product, aspects.
- Fetch evidence from a vector DB of normalized chunks.
- Rank evidence using: semantic similarity, source trust, recency, consensus.
- Return diverse, high-quality evidence.
Rules:
- Never invent text.
- Always include high-trust sources when available.
- Always include defect reports if found.
Output JSON:
{
"evidence": [...],
"diagnostics": {...}
}"""

class RetrieverAgent:
    def __init__(self, vector_db: VectorDBClient):
        self.client = LLMClient()
        self.agent_name = "retriever_agent" # Will map to 'bge-large-en' in config for embedding, but here we need the LLM for ranking?
        # Actually, the PRD lists "Retriever Agent" under "Technology and AI capability matrix" as using "bge-large-en".
        # But it also has a System Prompt, which implies an LLM step for ranking/selection/diagnostics.
        # The "Retriever Agent" in the Architecture Summary has a System Prompt.
        # So we likely use an LLM to process the raw retrieval results.
        # Let's use the 'planner' model or a specific 'retriever' LLM if defined, or default to gpt-4o-mini for efficiency?
        # The config has "primary_retrieval": "bge-large-en".
        # But the agent *logic* (ranking/diagnostics) needs an LLM. 
        # I will use the 'planner' model (GPT-4o-mini) or 'summarizer' for this reasoning step if not explicitly assigned an LLM in the matrix.
        # Wait, the matrix says "Retriever Agent" -> "bge-large-en". It doesn't list an LLM for it.
        # HOWEVER, the "Retriever Agent - System Prompt" exists. You can't send a system prompt to an embedding model.
        # So there MUST be an LLM involved to generate the "diagnostics" and "evidence" JSON from the raw chunks.
        # I will assume we use a standard LLM for this agent's reasoning layer.
        self.llm_agent_name = "retriever" # Reusing a lightweight model for this logic

        self.vector_db = vector_db

    def retrieve(self, context: ProductContext, plan: PlannerOutput) -> Dict[str, Any]:
        # 1. Execute retrieval based on plan
        # In a real system, we'd generate embeddings here.
        # For the mock, we just pass the text.
        
        query = f"{context.product_id} {context.user_question or ''} {' '.join(plan.aspects)}"
        
        # Fetch raw chunks
        raw_results = self.vector_db.query(query, top_k=10)
        
        # 2. Use LLM to rank and format (as per System Prompt)
        # We pass the raw results to the LLM and ask it to select/rank/diagnose.
        
        user_content = f"""
        Query: {query}
        Raw Retrieved Chunks:
        {json.dumps(raw_results, indent=2)}
        
        Plan Aspects: {plan.aspects}
        """
        
        response_str = self.client.generate_response(
            system_prompt=RETRIEVER_SYSTEM_PROMPT,
            user_content=user_content,
            agent_name=self.llm_agent_name
        )
        
        try:
            return json.loads(response_str)
        except json.JSONDecodeError:
            # Fallback if LLM fails
            return {"evidence": raw_results, "diagnostics": {"error": "LLM parsing failed"}}
