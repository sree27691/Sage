from sage.models.schemas import ProductContext, PlannerOutput
from sage.agents.retriever import RetrieverAgent
from sage.utils.vector_db import VectorDBClient
import datetime

def test_retriever():
    # Setup Mock DB
    db = VectorDBClient()
    db.add_documents([
        {"text": "The battery lasts 30 hours.", "source": "pdp", "metadata": {"trust": 1.0}},
        {"text": "Users report battery drains in 20 hours.", "source": "reddit", "metadata": {"trust": 0.6}},
        {"text": "Great sound quality.", "source": "youtube", "metadata": {"trust": 0.8}}
    ])

    # Setup Context and Plan
    context = ProductContext(
        product_id="test_product",
        url="http://test.com",
        pdp_html="",
        images=[],
        source="web_app",
        timestamp=datetime.datetime.now().isoformat(),
        user_question="How is the battery?"
    )
    
    plan = PlannerOutput(
        mode="standard",
        product_ids=["test_product"],
        aspects=["battery"],
        sources_to_use=["pdp", "reddit"],
        retrieval_config={},
        notes_for_summarizer=""
    )

    agent = RetrieverAgent(vector_db=db)
    result = agent.retrieve(context, plan)
    
    print("Retriever Result:")
    import json
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_retriever()
