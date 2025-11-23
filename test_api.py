from fastapi.testclient import TestClient
from main import app
from sage.models.schemas import ProductContext
import datetime

client = TestClient(app)

def test_api_flow():
    # 1. Test Web Ingest
    print("Testing /ingest/web...")
    response = client.post("/ingest/web", json={"url": "http://example.com/product"})
    assert response.status_code == 200
    web_context = response.json()["product_context"]
    print("Web Ingest Success")

    # 2. Test Extension Ingest
    print("Testing /ingest/extension...")
    response = client.post("/ingest/extension", json={
        "url": "http://example.com/product",
        "dom_html": "<html>...</html>",
        "images": ["http://img.com/1.jpg"],
        "extension_version": "1.0.0"
    })
    assert response.status_code == 200
    ext_context = response.json()["product_context"]
    print("Extension Ingest Success")

    # 3. Test Process
    print("Testing /process...")
    # Use the context from step 1
    response = client.post("/process", json={"product_context": web_context})
    if response.status_code != 200:
        print("Process Failed:", response.json())
    assert response.status_code == 200
    result = response.json()
    
    print("Process Result:")
    import json
    print(json.dumps(result, indent=2))
    
    assert "tcs_score" in result
    assert "trust_summary" in result

if __name__ == "__main__":
    test_api_flow()
