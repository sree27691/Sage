from sage.models.schemas import ProductContext
from sage.agents.vlm import VLMAgent
import datetime

def test_vlm():
    context = ProductContext(
        product_id="test_product",
        url="http://test.com",
        pdp_html="",
        images=["http://example.com/image1.jpg"],
        source="web_app",
        timestamp=datetime.datetime.now().isoformat()
    )

    agent = VLMAgent()
    result = agent.process_images(context)
    
    print("VLM Result:")
    import json
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_vlm()
