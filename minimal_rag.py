"""
minimal_rag.py RAG minimal working prototype
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Check OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    print(" Error: OPENAI_API_KEY not found in .env file")
    exit(1)

print("AlphaRAG - Minimal Working Prototype")
print("=" * 50)

# Import LlamaIndex with correct package names
try:
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
    from llama_index.llms.openai import OpenAI
    from llama_index.embeddings.openai import OpenAIEmbedding
    print("LlamaIndex imported successfully")
except ImportError as e:
    print(f"Import error: {e}")
    print("Installing missing packages...")
    import subprocess
    subprocess.run(["pip", "install", "llama-index-core", "llama-index-llms-openai", "llama-index-embeddings-openai"])
    print("Please run the script again")
    exit(1)

# Configure LlamaIndex
Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

def main():
    # Load documents
    print("\n Step 1: Loading documents...")
    
    data_dir = Path("data")
    if not data_dir.exists():
        print("No data/ directory. Run: python download_data.py")
        return
    
    try:
        documents = SimpleDirectoryReader("data").load_data()
        print(f"Loaded {len(documents)} documents")
        
        if len(documents) == 0:
            print(" No documents found. Run: python download_data.py")
            return
            
    except Exception as e:
        print(f" Error loading documents: {e}")
        return
    
    # Create index
    print("\n Step 2: Creating vector index...")
    start = time.time()
    index = VectorStoreIndex.from_documents(documents, show_progress=True)
    print(f"Index created in {time.time() - start:.2f}s")
    
    # Create query engine
    print("\n Step 3: Creating query engine...")
    query_engine = index.as_query_engine(similarity_top_k=5)
    print("Query engine ready!")
    
    # Test queries
    print("\n Step 4: Testing queries...")
    print("=" * 50)
    
    test_queries = [
        "What are the main risk factors?",
        "What is the revenue?",
        "What is the business strategy?",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n Query {i}: {query}")
        print("-" * 50)
        
        start = time.time()
        response = query_engine.query(query)
        latency = (time.time() - start) * 1000
        
        print(f" Answer: {response}")
        print(f" Latency: {latency:.0f}ms")
    
    print("\n" + "=" * 50)
    print(" Success! Your RAG system is working!")
    print("=" * 50)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
