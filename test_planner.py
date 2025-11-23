from sage.models.schemas import ProductContext
from sage.agents.planner import PlannerAgent
import datetime

def test_planner():
    context = ProductContext(
        product_id="test_product_123",
        url="https://example.com/product",
        pdp_html="<html>...</html>",
        images=["img1.jpg"],
        source="web_app",
        timestamp=datetime.datetime.now().isoformat(),
        user_question="Is the battery good?"
    )

    agent = PlannerAgent()
    plan = agent.plan(context)
    
    print("Planner Output:")
    print(plan.model_dump_json(indent=2))

if __name__ == "__main__":
    test_planner()
