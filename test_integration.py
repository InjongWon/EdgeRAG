"""
test_integration.py - Test full pipeline
"""

from src.ingestion.document_processor import DocumentProcessor
from src.ingestion.chunker import SemanticChunker
from llama_index.core import VectorStoreIndex, Document as LlamaDocument
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
import time

# Configure
Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

print("Testing integrated pipeline...")

# 1. Process document
processor = DocumentProcessor()
doc = processor.process("data/SAMPLE_TSLA_10K.txt")
print(f" Processed: {doc.source}")

# 2. Chunk document
chunker = SemanticChunker(chunk_size=256, chunk_overlap=30)
chunks = chunker.chunk_document(doc.text, doc.metadata)
print(f" Created {len(chunks)} chunks")

# 3. Convert to LlamaIndex format
llama_docs = [
    LlamaDocument(
        text=chunk.text,
        metadata={
            **chunk.metadata,
            "chunk_index": chunk.chunk_index,
            "source": doc.source
        }
    )
    for chunk in chunks
]

# 4. Index
print("Creating index...")
index = VectorStoreIndex.from_documents(llama_docs)
print(" Index created")

# 5. Query
query_engine = index.as_query_engine(similarity_top_k=3)

test_queries = [
    "What are the main risks?",
    "What is the revenue?",
    "What is the business strategy?"
]

print("\nTesting queries:")
print("=" * 50)

for query in test_queries:
    start = time.time()
    response = query_engine.query(query)
    latency = (time.time() - start) * 1000
    
    print(f"\n {query}")
    print(f" {str(response)[:200]}...")
    print(f" {latency:.0f}ms")

print("\n" + "=" * 50)
print(" Integration test passed!")
