"""
src/ingestion/document_processor.py - Document processing pipeline
"""

import pypdf
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import re

@dataclass
class Document:
    """Processed document"""
    text: str
    metadata: Dict
    pages: List[str]
    source: str

class DocumentProcessor:
    """Process PDF and text documents"""
    
    def __init__(self):
        self.supported_extensions = {'.pdf', '.txt', '.html'}
    
    def process(self, file_path: str) -> Document:
        """Process a document and extract text + metadata"""
        
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path.suffix not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {path.suffix}")
        
        # Extract text based on file type
        if path.suffix == '.pdf':
            pages, text = self._process_pdf(file_path)
        else:
            text = path.read_text(encoding='utf-8')
            pages = [text]
        
        # Clean text
        text = self._clean_text(text)
        
        # Extract metadata
        metadata = self._extract_metadata(text, path.name)
        
        return Document(
            text=text,
            metadata=metadata,
            pages=pages,
            source=path.name
        )
    
    def _process_pdf(self, pdf_path: str) -> tuple[List[str], str]:
        """Extract text from PDF"""
        
        try:
            reader = pypdf.PdfReader(pdf_path)
            pages = []
            
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    pages.append(page_text)
            
            full_text = "\n\n".join(pages)
            return pages, full_text
            
        except Exception as e:
            raise Exception(f"Error processing PDF: {e}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers (simple pattern)
        text = re.sub(r'Page \d+ of \d+', '', text)
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n')
        
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _extract_metadata(self, text: str, filename: str) -> Dict:
        """Extract document metadata"""
        
        metadata = {
            "filename": filename,
            "company": self._extract_company(text),
            "doc_type": self._extract_doc_type(text),
            "year": self._extract_year(text)
        }
        
        return metadata
    
    def _extract_company(self, text: str) -> Optional[str]:
        """Extract company name from document"""
        
        # Common patterns for company names in 10-Ks
        patterns = [
            r'([A-Z][A-Za-z\s&]+(?:Inc\.|LLC|Corp\.|Corporation|Ltd\.))',
            r'TESLA[,\s]INC',
            r'APPLE[,\s]INC',
            r'MICROSOFT[,\s]CORPORATION',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text[:1000])
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_doc_type(self, text: str) -> str:
        """Extract document type"""
        
        text_upper = text[:2000].upper()
        
        if '10-K' in text_upper:
            return '10-K'
        elif '10-Q' in text_upper:
            return '10-Q'
        elif '8-K' in text_upper:
            return '8-K'
        elif 'EARNINGS' in text_upper:
            return 'Earnings Call'
        else:
            return 'Unknown'
    
    def _extract_year(self, text: str) -> Optional[int]:
        """Extract fiscal year from document"""
        
        # Look for year patterns
        year_pattern = r'20[12]\d'
        matches = re.findall(year_pattern, text[:2000])
        
        if matches:
            # Return most recent year found
            years = [int(y) for y in matches]
            return max(years)
        
        return None

# Test function
if __name__ == "__main__":
    processor = DocumentProcessor()
    
    # Test with sample document
    import sys
    if len(sys.argv) > 1:
        doc = processor.process(sys.argv[1])
        print(f"Processed: {doc.source}")
        print(f"Pages: {len(doc.pages)}")
        print(f"Company: {doc.metadata['company']}")
        print(f"Type: {doc.metadata['doc_type']}")
        print(f"Year: {doc.metadata['year']}")
        print(f"Text length: {len(doc.text)} chars")
        print(f"\nFirst 500 chars:")
        print(doc.text[:500])
    else:
        print("Usage: python document_processor.py <file_path>")