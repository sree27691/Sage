# Sage Assistant

Sage is a multi-agent product truth engine designed to deliver unbiased, evidence-backed product intelligence.

## Project Structure

- **`sage/agents/`**: Contains the implementation of all agents (Planner, Retriever, VLM, Summarizer, Judge).
- **`sage/engine/`**: Contains the TCS (Truthful Coverage Score) Engine.
- **`sage/models/`**: Pydantic data models (`schemas.py`).
- **`sage/utils/`**: Utilities for LLM clients and Vector DB.
- **`config/`**: Configuration files (`models_config.json`).
- **`main.py`**: FastAPI application entry point.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn python-dotenv pydantic
   ```

2. **Environment Variables**:
   - Rename `.env` (if it exists as a template) or create one with your API keys:
     ```
     OPENAI_API_KEY=...
     GEMINI_API_KEY=...
     ...
     ```

## Running the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Documentation

Visit `http://127.0.0.1:8000/docs` to see the interactive Swagger UI.

### Key Endpoints

- **`POST /ingest/web`**: Ingest a product URL.
- **`POST /ingest/extension`**: Ingest data from the Chrome Extension.
- **`POST /process`**: Run the full analysis pipeline on a `ProductContext`.

## Next Steps (Moving to Production)

Currently, parts of the system use **Mock** implementations to allow for testing without live API keys or databases. To make this production-ready:

1.  **Real Vector DB**:
    - Update `sage/utils/vector_db.py` to connect to a real ChromaDB or Pinecone instance.
    - Implement actual embedding generation using the models defined in `config/models_config.json`.

2.  **Real LLM Calls**:
    - Update `sage/utils/llm_client.py` to make actual HTTP requests to OpenAI/Anthropic/Gemini APIs instead of returning mock JSON.

3.  **Data Fetching**:
    - Implement the actual scraping logic in `main.py` (for `/ingest/web`) to fetch HTML from URLs.

4.  **Frontend**:
    - Build the React/Next.js frontend for the Web App and the Chrome Extension popup.
