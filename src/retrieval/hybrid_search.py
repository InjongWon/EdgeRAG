from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import numpy as np

class HybridSearch:
    def __init__(self, use_docker=False):
        if use_docker:
            try:
                print("Connecting to Docker Qdrant...")
                self.qdrant = QdrantClient(host="localhost", port=6333)
                self.qdrant.get_collections()
                print(" Connected to Docker")
            except Exception as e:
                print(f" Docker failed: {e}")
                print("Using in-memory mode...")
                self.qdrant = QdrantClient(":memory:")
        else:
            print("⚡ Using in-memory Qdrant")
            self.qdrant = QdrantClient(":memory:")
            
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.bm25 = None
        self.documents = []
        
    def index_documents(self, chunks, metadata):
        # Create embeddings
        texts = [c.text for c in chunks]
        embeddings = self.encoder.encode(texts, show_progress_bar=True)
        
        # Create Qdrant collection
        self.qdrant.recreate_collection(
            collection_name="financial_docs",
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        
        # Index vectors
        points = [
            PointStruct(
                id=i,
                vector=embeddings[i].tolist(),
                payload={"text": chunks[i].text, **chunks[i].metadata}
            )
            for i in range(len(chunks))
        ]
        self.qdrant.upsert(collection_name="financial_docs", points=points)
        
        # Build BM25 index
        tokenized = [doc.split() for doc in texts]
        self.bm25 = BM25Okapi(tokenized)
        self.documents = texts
        
        print(f" Indexed {len(chunks)} chunks")
    
    def search(self, query, top_k=10, alpha=0.7):
        # Dense search
        query_emb = self.encoder.encode(query)
        dense_results = self.qdrant.query_points(collection_name ="financial_docs",
                                           query = query_emb.tolist(),
                                           limit = top_k *2).points
        
        # Sparse search
        bm25_scores = self.bm25.get_scores(query.split())
        
        # Combine scores
        combined = {}
        for r in dense_results:
            sparse = bm25_scores[r.id] if r.id < len(bm25_scores) else 0
            combined[r.id] = alpha * r.score + (1-alpha) * (sparse / max(bm25_scores))
        
        # Sort and return
        sorted_ids = sorted(combined.keys(), key=lambda x: combined[x], reverse=True)[:top_k]
        
        return [
            {
                "text": next(r for r in dense_results if r.id == i).payload["text"],
                "score": combined[i],
                "metadata": next(r for r in dense_results if r.id == i).payload
            }
            for i in sorted_ids
        ]