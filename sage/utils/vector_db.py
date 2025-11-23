import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import uuid
from sage.utils.chunking import Chunker
from sage.utils.embedding_client import EmbeddingClient

class VectorDBClient:
    def __init__(self, persist_path: str = "./sage_chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(name="sage_evidence")
        self.chunker = Chunker()
        self.embedder = EmbeddingClient()

    def clear_product(self, product_id: str):
        """
        Clear all data for a specific product from the vector DB.
        """
        try:
            # Delete all documents with this product_id
            results = self.collection.get(where={"product_id": product_id})
            if results and results['ids']:
                print(f"[VectorDB] Clearing {len(results['ids'])} chunks for product: {product_id}")
                self.collection.delete(ids=results['ids'])
        except Exception as e:
            print(f"[VectorDB] Error clearing product {product_id}: {e}")
    
    def clear_all(self):
        """
        Clear ALL data from the vector DB to ensure complete isolation.
        """
        try:
            # Get all IDs and delete them
            results = self.collection.get()
            if results and results['ids']:
                print(f"[VectorDB] Clearing ALL {len(results['ids'])} chunks from database")
                self.collection.delete(ids=results['ids'])
            else:
                print(f"[VectorDB] Database is already empty")
        except Exception as e:
            print(f"[VectorDB] Error clearing all data: {e}")

    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Adds documents to the store.
        Documents should have 'text', 'source_type', 'metadata', etc.
        We chunk them first, then embed, then store.
        """
        ids = []
        embeddings = []
        metadatas = []
        documents_text = []

        for doc in documents:
            raw_text = doc.get("text", "")
            source_type = doc.get("source_type", "unknown")
            base_metadata = doc.get("metadata", {})
            
            # 1. Chunk
            chunks = self.chunker.chunk(raw_text, source_type)
            
            # 2. Embed (Batching per doc for simplicity, ideally batch all)
            if not chunks:
                continue
                
            chunk_embeddings = self.embedder.get_text_embedding(chunks, "primary_retrieval")
            
            for i, chunk in enumerate(chunks):
                # Generate unique ID
                chunk_id = str(uuid.uuid4())
                
                ids.append(chunk_id)
                embeddings.append(chunk_embeddings[i])
                documents_text.append(chunk)
                
                # Merge metadata
                meta = base_metadata.copy()
                meta.update({
                    "source_type": source_type,
                    "chunk_index": i,
                    "parent_id": doc.get("evidence_id", "unknown")
                })
                metadatas.append(meta)

        # 3. Add to Chroma
        if ids:
            self.collection.add(
                documents=documents_text,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )

    def query(self, query_text: str, top_k: int = 5, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Semantic search using Chroma.
        """
        # 1. Embed Query
        query_embedding = self.embedder.get_text_embedding(query_text, "primary_retrieval")[0]
        
        # 2. Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filters # Chroma filters format
        )
        
        # 3. Format Results
        formatted_results = []
        if results["ids"]:
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "evidence_id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": results["distances"][0][i] if "distances" in results else 0.0
                })
                
        return formatted_results
