from typing import Dict, Any, List
from sage.models.schemas import ProductContext, TCSComponents, TrustSummary
from sage.agents.planner import PlannerAgent
from sage.agents.retriever import RetrieverAgent
from sage.agents.vlm import VLMAgent
from sage.agents.summarizer import SummarizerAgent
from sage.agents.judge import JudgeAgent
from sage.engine.tcs import TCSEngine
from sage.engine.tcs import TCSEngine
from sage.utils.vector_db import VectorDBClient
from sage.utils.external_search import ExternalSearch

class SagePipeline:
    def __init__(self):
        self.planner = PlannerAgent()
        self.vector_db = VectorDBClient() # In real app, this would be persistent
        self.retriever = RetrieverAgent(self.vector_db)
        self.vlm = VLMAgent()
        self.summarizer = SummarizerAgent()
        self.judge = JudgeAgent()
        self.summarizer = SummarizerAgent()
        self.judge = JudgeAgent()
        self.tcs_engine = TCSEngine()
        self.external_search = ExternalSearch()

    def run(self, context: ProductContext) -> Dict[str, Any]:
        print(f"[PIPELINE] ========================================")
        print(f"[PIPELINE] Starting NEW analysis")
        print(f"[PIPELINE] Product ID: {context.product_id}")
        print(f"[PIPELINE] URL: {context.url}")
        print(f"[PIPELINE] ========================================")
        
        # 0. CRITICAL: Clear ALL old data to ensure complete isolation
        print("[PIPELINE] Step 0: Clearing ALL old data from Vector DB...")
        self.vector_db.clear_all()  # Clear everything, not just this product
        
        # Add raw HTML (limited)
        if context.pdp_html:
            self.vector_db.add_documents([{
                "text": context.pdp_html[:50000],  # Limit to first 50k chars to avoid timeout
                "source_type": "pdp",
                "metadata": {
                    "url": context.url,
                    "product_id": context.product_id,
                    "title": context.metadata.get("title", "") if context.metadata else ""
                }
            }])
        
        # Add structured content (HIGH PRIORITY)
        if context.structured_content:
            print(f"[PIPELINE] Adding structured content: {list(context.structured_content.keys())}")
            for section_name, section_content in context.structured_content.items():
                if section_content:  # Only add non-null sections
                    self.vector_db.add_documents([{
                        "text": f"{section_name.replace('_', ' ').title()}: {section_content}",
                        "source_type": "structured_content",
                        "metadata": {
                            "url": context.url,
                            "product_id": context.product_id,
                            "section": section_name,
                            "priority": "high"  # Mark as high priority
                        }
                    }])
                    print(f"[PIPELINE]   - Added {section_name}: {len(section_content)} chars")
        
        print("[PIPELINE] Step 0: Complete - Vector DB populated with ONLY current product data")
        
        # 1. Planner
        print("[PIPELINE] Step 1: Planning...")
        plan = self.planner.plan(context)
        print(f"[PIPELINE] Step 1: Complete - Plan: {plan.mode}")
        
        # 2. Parallel Execution: Retriever + VLM
        print("[PIPELINE] Step 2: Retrieving evidence...")
        retrieval_result = self.retriever.retrieve(context, plan)
        evidence = retrieval_result.get("evidence", [])
        print(f"[PIPELINE] Step 2: Complete - Found {len(evidence)} evidence units")
        
        print("[PIPELINE] Step 3: Processing images...")
        vlm_result = self.vlm.process_images(context)
        if vlm_result.get("specs_detected"):
            evidence.append({
                "evidence_id": "vlm_1", 
                "text": f"Specs from image: {vlm_result['specs_detected']}", 
                "source_type": "vlm_image",
                "aspect_tags": ["specs"]
            })
        print(f"[PIPELINE] Step 3: Complete")
            
        # 2.5 External Search (Reddit & YouTube) - SKIP FOR NOW TO SPEED UP
        print("[PIPELINE] Step 4: Skipping external search (Reddit/YouTube) for speed...")
        # Commenting out to avoid timeout
        # query = (context.metadata or {}).get("title", "") or context.product_id
        # if query:
        #     reddit_results = self.external_search.search_reddit(query)
        #     ...
            
        # 3. Summarizer
        print("[PIPELINE] Step 5: Summarizing...")
        trust_summary = self.summarizer.summarize(context.product_id, evidence)
        print(f"[PIPELINE] Step 5: Complete")
        
        # 4. Judge
        print("[PIPELINE] Step 6: Judging claims...")
        judge_output = self.judge.judge(trust_summary, evidence)
        print(f"[PIPELINE] Step 6: Complete - {len(judge_output.claims_judgement)} claims judged")
        
        # 5. TCS Engine
        print("[PIPELINE] Step 7: Calculating TCS...")
        aspect_ontology = [a.name for a in trust_summary.aspects] if trust_summary.aspects else ["general"]
        
        tcs_result = self.tcs_engine.calculate_tcs(
            judge_output=judge_output,
            trust_summary=trust_summary,
            evidence_units=evidence,
            aspect_ontology=aspect_ontology
        )
        print(f"[PIPELINE] Step 7: Complete - TCS: {tcs_result.tcs_score}")
        
        print("[PIPELINE] Analysis complete!")
        return {
            "product_id": context.product_id,
            "tcs_score": tcs_result.tcs_score,
            "tcs_band": tcs_result.band,
            "tcs_components": tcs_result.model_dump(),
            "trust_summary": trust_summary.model_dump(),
            "diagnostics": retrieval_result.get("diagnostics", {})
        }
