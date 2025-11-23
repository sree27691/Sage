from sage.utils.embedding_client import EmbeddingClient
import os

def test_embeddings():
    client = EmbeddingClient()
    
    print("--- Testing Embedding Client ---")
    
    text = "This is a test sentence."
    
    # 1. Primary Retrieval (BGE - likely mock if lib missing)
    print("\nTesting Primary Retrieval (BGE)...")
    emb = client.get_text_embedding(text, "primary_retrieval")
    print(f"Embedding shape: {len(emb[0])} dimensions")
    
    # 2. Redundancy Layer (OpenAI)
    if os.getenv("OPENAI_API_KEY"):
        print("\nTesting Redundancy Layer (OpenAI)...")
        try:
            emb = client.get_text_embedding(text, "redundancy_layer")
            print(f"Embedding shape: {len(emb[0])} dimensions")
        except Exception as e:
            print(f"OpenAI failed: {e}")
    else:
        print("\nSkipping OpenAI (Key not found)")

if __name__ == "__main__":
    test_embeddings()
