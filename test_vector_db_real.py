from sage.utils.vector_db import VectorDBClient
import shutil
import os

def test_real_vector_db():
    # Clean up previous test db if exists
    if os.path.exists("./sage_chroma_db_test"):
        shutil.rmtree("./sage_chroma_db_test")

    print("--- Testing Real Vector DB (Chroma) ---")
    
    # Initialize with test path
    db = VectorDBClient(persist_path="./sage_chroma_db_test")
    
    # Add Documents
    docs = [
        {
            "text": "The battery life of the Sony XM5 is amazing, lasting over 30 hours.",
            "source_type": "reviews",
            "metadata": {"author": "User123"}
        },
        {
            "text": "However, the noise cancellation is slightly worse than the XM4.",
            "source_type": "reviews",
            "metadata": {"author": "User456"}
        }
    ]
    
    print(f"Adding {len(docs)} documents...")
    db.add_documents(docs)
    
    # Query
    query = "How is the battery?"
    print(f"\nQuerying: '{query}'")
    results = db.query(query, top_k=2)
    
    for res in results:
        print(f"- [Score: {res['score']:.4f}] {res['text']} (Source: {res['metadata']['source_type']})")

    # Clean up
    if os.path.exists("./sage_chroma_db_test"):
        shutil.rmtree("./sage_chroma_db_test")

if __name__ == "__main__":
    test_real_vector_db()
