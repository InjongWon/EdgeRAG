"""
cached_rag.py - Add caching to your existing RAG for 5x speedup!

This uses your Day 1 setup + adds caching = HUGE performance win
"""

import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# Import our cache
import sys
sys.path.insert(0, str(Path.cwd()))
from src.optimization.simple_cache import SimpleSemanticCache

# Configure LlamaIndex
Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

class CachedRAGPipeline:
    """RAG Pipeline with Semantic Caching"""
    
    def __init__(self):
        print(" Initializing Cached RAG Pipeline...")
        
        # Load documents
        print("  Loading documents...")
        documents = SimpleDirectoryReader("data").load_data()
        print(f"   Loaded {len(documents)} documents")
        
        # Create index
        print("  Creating index...")
        self.index = VectorStoreIndex.from_documents(documents, show_progress=False)
        self.query_engine = self.index.as_query_engine(similarity_top_k=5)
        print("   Index ready")
        
        # Initialize cache
        self.cache = SimpleSemanticCache(similarity_threshold=0.95)
        print("   Cache initialized")
        
        print("\n Pipeline ready!\n")
    
    def query(self, query_text: str, use_cache: bool = True):
        """Query with optional caching"""
        
        start_time = time.time()
        
        # Check cache first
        if use_cache:
            cached_result = self.cache.get(query_text)
            if cached_result:
                latency = (time.time() - start_time) * 1000
                return {
                    "answer": cached_result,
                    "latency_ms": latency,
                    "cache_hit": True
                }
        
        # Cache miss - compute result
        response = self.query_engine.query(query_text)
        answer = str(response)
        
        # Store in cache
        if use_cache:
            self.cache.set(query_text, answer)
        
        latency = (time.time() - start_time) * 1000
        
        return {
            "answer": answer,
            "latency_ms": latency,
            "cache_hit": False
        }
    
    def get_stats(self):
        """Get cache statistics"""
        return self.cache.stats()


def main():
    print(" Cached RAG Demo - See the 5x Speedup!")
    print("=" * 70)
    
    # Initialize pipeline
    pipeline = CachedRAGPipeline()
    
    # Test queries (including duplicates to show caching)
    test_queries = [
        "What are the main risk factors?",
        "What is the revenue?",
        "What are the main risks?",  # Similar to #1
        "What is the business strategy?",
        "What are the risk factors?",  # Similar to #1 again
        "What is the revenue in 2023?",  # Similar to #2
        "Who are the competitors?",
        "What are the main risks?",  # Duplicate
    ]
    
    print(f"\n Running {len(test_queries)} queries (some duplicates)...\n")
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. {query}")
        result = pipeline.query(query)
        results.append(result)
        
        # Show result
        if result["cache_hit"]:
            print(f"    {result['latency_ms']:.0f}ms (CACHED)")
        else:
            print(f"    {result['latency_ms']:.0f}ms (computed)")
        print(f"    {result['answer'][:100]}...")
        print()
    
    # Show statistics
    print("=" * 70)
    print(" PERFORMANCE RESULTS")
    print("=" * 70)
    
    cached_latencies = [r['latency_ms'] for r in results if r['cache_hit']]
    uncached_latencies = [r['latency_ms'] for r in results if not r['cache_hit']]
    
    stats = pipeline.get_stats()
    
    print(f"\nCache Performance:")
    print(f"  Hits: {stats['hits']}")
    print(f"  Misses: {stats['misses']}")
    print(f"  Hit Rate: {stats['hit_rate']:.1%}")
    
    if cached_latencies and uncached_latencies:
        import numpy as np
        avg_cached = np.mean(cached_latencies)
        avg_uncached = np.mean(uncached_latencies)
        speedup = avg_uncached / avg_cached
        
        print(f"\nLatency Comparison:")
        print(f"  Cached queries:   {avg_cached:.0f}ms")
        print(f"  Uncached queries: {avg_uncached:.0f}ms")
        print(f"  Speedup: {speedup:.1f}x faster! 🚀")
        
        savings = (stats['hits'] / stats['total']) * 100
        print(f"  {savings:.0f}% of queries avoided API calls")
    
    print("\n" + "=" * 70)
    print(" This is your Day 3 deliverable - DONE!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n Interrupted.")
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()