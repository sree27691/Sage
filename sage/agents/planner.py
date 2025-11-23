import json
from typing import Dict, Any
from sage.models.schemas import ProductContext, PlannerOutput
from sage.utils.llm_client import LLMClient

PLANNER_SYSTEM_PROMPT = """You are the Planner Agent for Sage, a product truth engine.
Your job is to:
- Understand product context from URLs, PDP snapshots, or user questions.
- Decide which sources to use: PDP/specs, YouTube reviews, Reddit posts, lab reports,
images, manuals.
- Decide which aspects matter for this question (sound, ANC, comfort, mic, build, battery,
connectivity, warranty, defects, alternatives).
- Determine cold-start vs warm-start retrieval.
- Produce a plan that downstream agents must follow exactly.
Rules:
- Always prefer cached evidence where possible.
- Only request ingestion when required.
- Never generate final answers—only structured plans.
Output (JSON):
{
"mode": "...",
"product_ids": [...],
"aspects": [...],
"sources_to_use": [...],
"retrieval_config": {...},
"notes_for_summarizer": "..."
}"""

class PlannerAgent:
    def __init__(self):
        self.client = LLMClient()
        self.agent_name = "planner"

    def plan(self, context: ProductContext) -> PlannerOutput:
        # Construct the user content from the ProductContext
        user_content = f"""
        Product Context:
        Product ID: {context.product_id}
        URL: {context.url}
        Source: {context.source}
        User Question: {context.user_question}
        """
        
        response_str = self.client.generate_response(
            system_prompt=PLANNER_SYSTEM_PROMPT,
            user_content=user_content,
            agent_name=self.agent_name,
            response_format=PlannerOutput
        )
        
        # Parse the response into the Pydantic model
        try:
            data = json.loads(response_str)
            return PlannerOutput(**data)
        except json.JSONDecodeError:
            # Handle error or retry
            raise ValueError("Failed to parse LLM response")
