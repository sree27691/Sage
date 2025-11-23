import os
import json
from typing import List, Union
from dotenv import load_dotenv
from openai import OpenAI

# Try importing sentence_transformers, handle if missing
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

load_dotenv()

class EmbeddingClient:
    def __init__(self):
        self.models_config = self._load_models_config()
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None
        
        # Initialize local models if available
        self.local_models = {}
        
    def _load_models_config(self):
        config_path = os.path.join(os.path.dirname(__file__), "../../config/models_config.json")
        with open(config_path, "r") as f:
            return json.load(f)

    def get_text_embedding(self, text: Union[str, List[str]], model_usage: str = "primary_retrieval") -> List[List[float]]:
        """
        Get embeddings for text.
        model_usage: 'primary_retrieval' (BGE) or 'redundancy_layer' (OpenAI)
        """
        model_name = self.models_config.get("embedding_models", {}).get(model_usage, "bge-large-en")
        
        if isinstance(text, str):
            text = [text]

        if "openai" in model_name.lower() or "text-embedding" in model_name.lower():
            return self._get_openai_embedding(text, model_name)
        else:
            # Assume local model (e.g., BGE)
            return self._get_local_embedding(text, model_name)

    def _get_openai_embedding(self, texts: List[str], model: str) -> List[List[float]]:
        if not self.openai_client:
            raise ValueError("OpenAI API key not found for embeddings.")
        
        # OpenAI handles batching, but robust code might batch manually if list is huge
        response = self.openai_client.embeddings.create(input=texts, model=model)
        return [data.embedding for data in response.data]

    def _get_local_embedding(self, texts: List[str], model_name: str) -> List[List[float]]:
        if not HAS_SENTENCE_TRANSFORMERS:
            print(f"Warning: sentence-transformers not installed. Returning mock embeddings for {model_name}.")
            return [[0.1] * 768 for _ in texts] # Mock 768-dim embedding
            
        if model_name not in self.local_models:
            print(f"Loading local model: {model_name}...")
            self.local_models[model_name] = SentenceTransformer(model_name)
            
        embeddings = self.local_models[model_name].encode(texts)
        return embeddings.tolist()

    def get_image_embedding(self, image_paths: List[str]) -> List[List[float]]:
        """
        Get embeddings for images using OpenCLIP or similar.
        For now, this is a placeholder/mock unless we install open_clip.
        """
        # Real implementation would use open_clip or similar library
        print("Image embedding not fully implemented. Returning mock.")
        return [[0.1] * 512 for _ in image_paths]
