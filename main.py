from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import datetime
from sage.models.schemas import ProductContext
from sage.pipeline import SagePipeline

from sage.utils.scraper import WebScraper

# ... (imports)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sage Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (including Chrome extensions)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Pipeline and Scraper
pipeline = SagePipeline()
scraper = WebScraper()

# Request Models
class WebIngestRequest(BaseModel):
    url: str
    timestamp: Optional[str] = None

class ExtensionIngestRequest(BaseModel):
    url: str
    dom_html: str
    images: List[str]
    reviews_html: Optional[str] = None
    structured_content: Optional[Dict[str, Optional[str]]] = None
    extension_version: str
    timestamp: Optional[str] = None

class ProcessRequest(BaseModel):
    product_context: ProductContext


@app.post("/ingest/web")
async def ingest_web(request: WebIngestRequest):
    try:
        context = scraper.scrape(request.url)
        return {"status": "success", "product_context": context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.post("/ingest/extension")
async def ingest_extension(request: ExtensionIngestRequest):
    try:
        print(f"[INGEST] Received request from extension v{request.extension_version}")
        print(f"[INGEST] URL: {request.url}")
        print(f"[INGEST] DOM size: {len(request.dom_html)} chars")
        print(f"[INGEST] Images: {len(request.images)}")
        print(f"[INGEST] Structured content: {list(request.structured_content.keys()) if request.structured_content else 'None'}")
        
        # Generate unique product_id from URL
        import hashlib
        product_id = hashlib.md5(request.url.encode()).hexdigest()[:16]
        print(f"[INGEST] Generated product_id: {product_id}")
        
        context = ProductContext(
            product_id=product_id,  # Use URL-based unique ID
            url=request.url,
            pdp_html=request.dom_html,
            images=request.images,
            reviews_html=request.reviews_html,
            structured_content=request.structured_content,
            source="browser_extension",
            timestamp=request.timestamp or datetime.datetime.now().isoformat()
        )
        print(f"[INGEST] ProductContext created successfully")
        return {"status": "success", "product_context": context}
    except Exception as e:
        import traceback
        print(f"[INGEST ERROR] {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")



class ChatRequest(BaseModel):
    product_context: ProductContext
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Simple Chat Logic: Use Summarizer model to answer based on context
        # In a real app, we might want a dedicated ChatAgent with history
        
        # Construct context from the product info
        # We use the PDP HTML or text if available, but for efficiency we might just use metadata + summary if available
        # For now, let's pass the raw text from the context if it's not too huge, or just the metadata
        
        # Extract text from PDP HTML for context
        product_text = "No product details available."
        if request.product_context.pdp_html:
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(request.product_context.pdp_html, 'html.parser')
                # Remove script and style elements
                for script in soup(["script", "style", "header", "footer", "nav"]):
                    script.extract()
                text = soup.get_text(separator='\n')
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text_clean = '\n'.join(chunk for chunk in chunks if chunk)
                # Limit to first 15000 chars to fit in context
                product_text = text_clean[:15000]
            except Exception as e:
                print(f"Error extracting text for chat: {e}")
                product_text = "Error parsing product details."

        context_str = f"""
        Product: {request.product_context.product_id}
        Title: {request.product_context.metadata.get('title', 'Unknown') if request.product_context.metadata else 'Unknown'}
        URL: {request.product_context.url}
        
        Product Details:
        {f"--- Structured Content ---\n{request.product_context.structured_content}\n--------------------------" if request.product_context.structured_content else ""}
        
        {product_text}
        
        User Question: {request.message}
        """
        
        # We can reuse the LLMClient directly
        from sage.utils.llm_client import LLMClient
        llm_client = LLMClient()
        
        system_prompt = """You are Sage, a helpful product assistant.
        Answer the user's question based ONLY on the provided product context.
        If you don't know, say so. Keep answers concise and helpful."""
        
        response = llm_client.generate_response(
            system_prompt=system_prompt,
            user_content=context_str,
            agent_name="chat"
        )
        
        return {"response": response}
    except Exception as e:
        import traceback
        print(f"ERROR in /chat: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process")
async def process(request: ProcessRequest):
    try:
        result = pipeline.run(request.product_context)
        return result
    except Exception as e:
        import traceback
        print(f"ERROR in /process: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
