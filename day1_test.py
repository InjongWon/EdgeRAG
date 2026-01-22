"""
day1_test.py - Day 1 Complete Test

This tests that your basic RAG pipeline is working end-to-end.
Run this at the end of Day 1 to verify success!
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

print(" AlphaRAG Day 1 - Complete System Test")
print("=" * 60)

# Check 1: Environment
print("\n✓ Check 1: Environment Setup")
if not os.getenv("OPENAI_API_KEY"):
    print("   OPENAI_API_KEY not set")
    sys.exit(1)
print("   API key configured")

# Check 2: Dependencies
print("\n✓ Check 2: Dependencies")
try:
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    print("   LlamaIndex installed")
except ImportError as e:
    print(f"   LlamaIndex missing: {e}")
    sys.exit(1)

try:
    import pypdf
    print("   PyPDF installed")
except ImportError:
    print("   PyPDF missing")
    sys.exit(1)

# Check 3: Data
print("\n✓ Check 3: Data Files")
data_dir = Path("data")
if not data_dir.exists():
    print("   data/ directory missing")
    sys.exit(1)

files = list(data_dir.glob("*.txt")) + list(data_dir.glob("*.pdf"))
if not files:
    print("   No documents found in data/")
    print("  → Run: python download_data.py")
    sys.exit(1)

print(f"   Found {len(files)} documents")
for f in files[:3]:
    print(f"     - {f.name}")

# Check 4: Document Processing
print("\n✓ Check 4: Document Processing")
try:
    sys.path.insert(0, str(Path.cwd()))
    from src.ingestion.document_processor import DocumentProcessor
    from src.ingestion.chunker import SemanticChunker
    
    processor = DocumentProcessor()
    doc = processor.process(str(files[0]))
    
    print(f"   Processed {doc.source}")
    print(f"     - Pages: {len(doc.pages)}")
    print(f"     - Company: {doc.metadata.get('company', 'Unknown')}")
    print(f"     - Text length: {len(doc.text)} chars")
    
    chunker = SemanticChunker(chunk_size=512)
    chunks = chunker.chunk_document(doc.text, doc.metadata)
    print(f"   Created {len(chunks)} chunks")
    
except Exception as e:
    print(f"   Processing failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check 5: RAG Pipeline
print("\n✓ Check 5: RAG Pipeline")
try:
    import time
    from llama_index.core import Settings
    from llama_index.llms.openai import OpenAI
    from llama_index.embeddings.openai import OpenAIEmbedding
    
    Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
    
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents[:3], show_progress=False)  # Use first 3 docs for speed
    query_engine = index.as_query_engine(similarity_top_k=3)
    
    # Test query
    test_query = "What are the main risks?"
    start = time.time()
    response = query_engine.query(test_query)
    latency = (time.time() - start) * 1000
    
    print(f"   RAG pipeline working")
    print(f"     - Query: {test_query}")
    print(f"     - Response: {str(response)[:150]}...")
    print(f"     - Latency: {latency:.0f}ms")
    
except Exception as e:
    print(f"  RAG pipeline failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Success!
print("\n" + "=" * 60)
print(" SUCCESS! All Day 1 checks passed!")
print("=" * 60)

print("\n Summary:")
print(f"   Environment configured")
print(f"   Dependencies installed")
print(f"  {len(files)} documents ready")
print(f"   Document processing working")
print(f"   RAG pipeline functional")

print("\n Next Steps (Day 2):")
print("  1. Build hybrid search (dense + sparse)")
print("  2. Add reranking")
print("  3. Implement vector database (Qdrant)")
print("  4. Create proper API endpoints")

print("\n Try the interactive demo:")
print("  python minimal_rag.py")