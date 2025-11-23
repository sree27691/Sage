from sage.models.schemas import ProductContext, PlannerOutput
from sage.agents.retriever import RetrieverAgent
from sage.agents.summarizer import SummarizerAgent
from sage.agents.judge import JudgeAgent
from sage.engine.tcs import TCSEngine
from sage.utils.vector_db import VectorDBClient
import datetime
import json

def test_pipeline():
    print("1. Setting up Context...")
    context = ProductContext(
        product_id="test_product",
        url="http://test.com",
        pdp_html="",
        images=[],
        source="web_app",
        timestamp=datetime.datetime.now().isoformat(),
        user_question="How is the battery?"
    )
    
    # Mock Plan (skipping Planner Agent call for brevity, using object directly)
    plan = PlannerOutput(
        mode="standard",
        product_ids=["test_product"],
        aspects=["battery", "sound"],
        sources_to_use=["pdp", "youtube"],
        retrieval_config={},
        notes_for_summarizer=""
    )
    
    print("2. Running Retriever...")
    db = VectorDBClient()
    # Add some dummy evidence that matches the mock judge expectations
    db.add_documents([
        {"text": "Battery lasts 30 hours", "source_type": "pdp", "evidence_id": "1", "aspect_tags": ["battery"]},
        {"text": "Sound is great", "source_type": "youtube", "evidence_id": "2", "aspect_tags": ["sound"]}
    ])
    retriever = RetrieverAgent(vector_db=db)
    retrieval_result = retriever.retrieve(context, plan)
    evidence = retrieval_result.get("evidence", [])
    
    print("3. Running Summarizer...")
    summarizer = SummarizerAgent()
    trust_summary = summarizer.summarize(context.product_id, evidence)
    
    print("4. Running Judge...")
    judge = JudgeAgent()
    judge_output = judge.judge(trust_summary, evidence)
    
    print("5. Running TCS Engine...")
    tcs_engine = TCSEngine()
    aspect_ontology = ["battery", "sound", "durability"]
    
    tcs_result = tcs_engine.calculate_tcs(
        judge_output=judge_output,
        trust_summary=trust_summary,
        evidence_units=evidence,
        aspect_ontology=aspect_ontology
    )
    
    print("\n--- Final TCS Result ---")
    print(tcs_result.model_dump_json(indent=2))

if __name__ == "__main__":
    test_pipeline()
