from src.ingestion import DocumentProcessor, SemanticChunker
from src.retrieval.hybrid_search import HybridSearch
from pathlib import Path

# Process documents
processor = DocumentProcessor()
chunker = SemanticChunker()

all_chunks = []
for file in Path("data").glob("*.txt"):
    doc = processor.process(str(file))
    chunks = chunker.chunk_document(doc.text, doc.metadata)
    all_chunks.extend(chunks)

# Index - USE IN-MEMORY MODE (no Docker!)
search = HybridSearch(use_docker=False)  # ← Changed this line
search.index_documents(all_chunks, {})

# Search
results = search.search("What are the main risks?", top_k=5)
for i, r in enumerate(results):
    print(f"{i+1}. Score: {r['score']:.3f}")
    print(f"   {r['text'][:150]}...")