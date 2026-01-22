"""
src/optimization/simple_cache.py - Simple in-memory semantic cache

NO DOCKER NEEDED - Works immediately!
"""

from sentence_transformers import SentenceTransformer
import numpy as np
import time
from typing import Optional, Any, Dict

class SimpleSemanticCache:
    """In-memory semantic cache - blazing fast!"""
    
    def __init__(self, similarity_threshold=0.95, max_size=1000):
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.cache = {}  # {query_hash: {"embedding": emb, "result": result, "timestamp": time}}
        self.threshold = similarity_threshold
        self.max_size = max_size
        
        # Stats
        self.hits = 0
        self.misses = 0
    
    def get(self, query: str) -> Optional[Any]:
        """Check if query is in cache"""
        
        query_emb = self.encoder.encode(query)
        
        # Check all cached queries
        for cached_query, data in self.cache.items():
            similarity = self._cosine_similarity(query_emb, data["embedding"])
            
            if similarity >= self.threshold:
                self.hits += 1
                print(f"  🎯 Cache HIT (similarity: {similarity:.3f})")
                return data["result"]
        
        self.misses += 1
        return None
    
    def set(self, query: str, result: Any):
        """Store result in cache"""
        
        # Limit cache size (simple FIFO)
        if len(self.cache) >= self.max_size:
            oldest = min(self.cache.items(), key=lambda x: x[1]["timestamp"])
            del self.cache[oldest[0]]
        
        query_emb = self.encoder.encode(query)
        query_hash = hash(query)
        
        self.cache[query_hash] = {
            "embedding": query_emb,
            "result": result,
            "timestamp": time.time()
        }
    
    def _cosine_similarity(self, a, b):
        """Compute cosine similarity"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def stats(self) -> Dict:
        """Get cache statistics"""
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total": total,
            "hit_rate": self.hits / total if total > 0 else 0,
            "cache_size": len(self.cache)
        }
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0


# Test
if __name__ == "__main__":
    print("🧪 Testing Simple Semantic Cache")
    print("=" * 60)
    
    cache = SimpleSemanticCache(similarity_threshold=0.95)
    
    # Test 1: Cache miss
    print("\n1. First query (cache miss)")
    result = cache.get("What are the risks?")
    print(f"   Result: {result}")
    
    # Store result
    cache.set("What are the risks?", "Risk factors include supply chain, competition...")
    
    # Test 2: Exact match (cache hit)
    print("\n2. Same query (cache hit)")
    result = cache.get("What are the risks?")
    print(f"   Result: {result}")
    
    # Test 3: Similar query (cache hit)
    print("\n3. Similar query (cache hit)")
    result = cache.get("What are the main risk factors?")
    print(f"   Result: {result}")
    
    # Test 4: Different query (cache miss)
    print("\n4. Different query (cache miss)")
    result = cache.get("What is the revenue?")
    print(f"   Result: {result}")
    
    # Stats
    print("\n" + "=" * 60)
    stats = cache.stats()
    print(f"Cache Statistics:")
    print(f"  Hits: {stats['hits']}")
    print(f"  Misses: {stats['misses']}")
    print(f"  Hit Rate: {stats['hit_rate']:.1%}")
    print(f"  Cache Size: {stats['cache_size']}")