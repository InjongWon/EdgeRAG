"""
src/ingestion/chunker.py - Intelligent document chunking
"""

from typing import List
from dataclasses import dataclass
import re

@dataclass
class Chunk:
    """Text chunk with metadata"""
    text: str
    chunk_index: int
    start_char: int
    end_char: int
    metadata: dict

class SemanticChunker:
    """Chunk documents intelligently preserving semantic meaning"""
    
    def __init__(
        self, 
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        min_chunk_size: int = 100
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
    
    def chunk_document(self, text: str, metadata: dict = None) -> List[Chunk]:
        """Chunk document using sentence-aware strategy"""
        
        if metadata is None:
            metadata = {}
        
        # Split into sentences
        sentences = self._split_sentences(text)
        
        # Group sentences into chunks
        chunks = []
        current_chunk = []
        current_length = 0
        char_position = 0
        
        for sentence in sentences:
            sentence_words = sentence.split()
            sentence_length = len(sentence_words)
            
            # Check if adding this sentence exceeds chunk size
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = " ".join(current_chunk)
                start_char = char_position
                end_char = start_char + len(chunk_text)
                
                chunks.append(Chunk(
                    text=chunk_text,
                    chunk_index=len(chunks),
                    start_char=start_char,
                    end_char=end_char,
                    metadata={**metadata, "chunk_size": len(chunk_text.split())}
                ))
                
                # Create overlap: keep last N sentences
                overlap_sentences = self._get_overlap_sentences(
                    current_chunk, 
                    self.chunk_overlap
                )
                
                # Start new chunk with overlap
                current_chunk = overlap_sentences + [sentence]
                current_length = sum(len(s.split()) for s in current_chunk)
                char_position = end_char
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        # Add final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(Chunk(
                text=chunk_text,
                chunk_index=len(chunks),
                start_char=char_position,
                end_char=char_position + len(chunk_text),
                metadata={**metadata, "chunk_size": len(chunk_text.split())}
            ))
        
        # Merge small chunks
        chunks = self._merge_small_chunks(chunks)
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        
        # Simple sentence splitting (can be improved with spaCy/NLTK)
        # Split on . ! ? followed by space and capital letter
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        
        # Clean up sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _get_overlap_sentences(self, sentences: List[str], target_words: int) -> List[str]:
        """Get last N words worth of sentences for overlap"""
        
        overlap = []
        word_count = 0
        
        # Work backwards through sentences
        for sentence in reversed(sentences):
            sentence_words = len(sentence.split())
            if word_count + sentence_words <= target_words:
                overlap.insert(0, sentence)
                word_count += sentence_words
            else:
                break
        
        return overlap
    
    def _merge_small_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """Merge chunks that are too small"""
        
        if not chunks:
            return chunks
        
        merged = []
        i = 0
        
        while i < len(chunks):
            current = chunks[i]
            current_size = len(current.text.split())
            
            # If chunk is too small and there's a next chunk, merge
            if current_size < self.min_chunk_size and i < len(chunks) - 1:
                next_chunk = chunks[i + 1]
                merged_text = f"{current.text} {next_chunk.text}"
                
                merged.append(Chunk(
                    text=merged_text,
                    chunk_index=len(merged),
                    start_char=current.start_char,
                    end_char=next_chunk.end_char,
                    metadata={**current.metadata, "merged": True}
                ))
                i += 2  # Skip next chunk since we merged it
            else:
                # Re-index
                merged.append(Chunk(
                    text=current.text,
                    chunk_index=len(merged),
                    start_char=current.start_char,
                    end_char=current.end_char,
                    metadata=current.metadata
                ))
                i += 1
        
        return merged

# Test function
if __name__ == "__main__":
    # Test chunking
    sample_text = """
    Tesla, Inc. designs, develops, manufactures, and sells electric vehicles. 
    The company was founded in 2003 and is headquartered in Austin, Texas. 
    Tesla's mission is to accelerate the world's transition to sustainable energy.
    
    The company faces several key risks. Supply chain disruptions could impact production.
    Competition in the EV market is intensifying rapidly. Regulatory changes could 
    increase costs or limit operations.
    
    Revenue for fiscal year 2023 was $96.7 billion, up 19% from prior year.
    Operating margin improved to 9.2% from 8.5% in the previous year.
    """
    
    chunker = SemanticChunker(chunk_size=50, chunk_overlap=10)
    chunks = chunker.chunk_document(sample_text, {"source": "test"})
    
    print(f"Created {len(chunks)} chunks:\n")
    for chunk in chunks:
        print(f"Chunk {chunk.chunk_index}:")
        print(f"  Size: {len(chunk.text.split())} words")
        print(f"  Text: {chunk.text[:100]}...")
        print()