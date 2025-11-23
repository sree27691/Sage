import json
from typing import List, Dict, Any
from sage.models.schemas import TrustSummary, JudgeOutput
from sage.utils.llm_client import LLMClient

JUDGE_SYSTEM_PROMPT = """You are the Judge Agent for Sage.
Your job is to:
- Evaluate each claim strictly against the provided evidence.
- Detect contradictions between different evidence sources (e.g., PDP says X, Reviews say Y).
- Flag missing evidence or weak support.
- Mark doubtful cases as Unsupported.
- Identify conflicts and uncertainties explicitly.
Output JSON:
{
"claims_judgement": [
    {"claim_text": "...", "evidence_ids": ["..."], "judge_label": "Supported|PartiallySupported|Unsupported|Contradicted", "reasoning": "..."}
],
"conflicts": ["Conflict description..."],
"uncertainty_aspects": ["Aspect name..."]
}"""

class JudgeAgent:
    def __init__(self):
        self.client = LLMClient()
        self.agent_name = "judge"

    def judge(self, trust_summary: TrustSummary, evidence: List[Dict[str, Any]]) -> JudgeOutput:
        user_content = f"""
        Trust Summary Claims: {trust_summary.claims}
        Evidence Bundle:
        {json.dumps(evidence, indent=2)}
        """
        
        response_str = self.client.generate_response(
            system_prompt=JUDGE_SYSTEM_PROMPT,
            user_content=user_content,
            agent_name=self.agent_name,
            response_format=JudgeOutput,
            temperature=0.0
        )
        
        try:
            data = json.loads(response_str)
            return JudgeOutput(**data)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse Judge response")
