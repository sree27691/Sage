import json
from typing import List, Dict, Any
from sage.models.schemas import ProductContext
from sage.utils.llm_client import LLMClient

VLM_SYSTEM_PROMPT = """You are the VLM Image/OCR Agent for Sage.
Your job is to:
- Extract structured information from product images.
- Identify spec badges (LDAC, Hi‑Res, IP ratings), ports, buttons, model identifiers.
- Recognize manual text and convert it into structured JSON.
- Never hallucinate unseen items.
- Mark uncertain fields as null with 'low_confidence'.
Output JSON:
{
"captions": [...],
"specs_detected": [...],
"model_strings": [...],
"ports": [...],
"manual_text": "...",
"confidence_scores": {...}
}"""

class VLMAgent:
    def __init__(self):
        self.client = LLMClient()
        self.agent_name = "vlm_ocr"

    def process_images(self, context: ProductContext) -> Dict[str, Any]:
        if not context.images:
            return {
                "captions": [],
                "specs_detected": [],
                "model_strings": [],
                "ports": [],
                "manual_text": None,
                "confidence_scores": {}
            }

        # In a real implementation, we would pass image bytes/URLs to the VLM.
        # Here we simulate by passing a description of the images or just the list of URLs
        # and letting the mock LLM client handle it (or return a mock response).
        
        user_content = f"""
        Product ID: {context.product_id}
        Images to process: {context.images}
        """
        
        response_str = self.client.generate_response(
            system_prompt=VLM_SYSTEM_PROMPT,
            user_content=user_content,
            agent_name=self.agent_name
        )
        
        try:
            return json.loads(response_str)
        except json.JSONDecodeError:
            return {"error": "Failed to parse VLM response"}
