from typing import List
import re
from config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SemanticChunker:
    """Semantic text chunking for better context retrieval."""
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """Chunk text using semantic boundaries."""
        # First, try to split by semantic boundaries
        chunks = self._split_by_semantic_boundaries(text)
        
        # If chunks are too large, apply size-based splitting
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > self.chunk_size:
                final_chunks.extend(self._split_by_size(chunk))
            else:
                final_chunks.append(chunk)
        
        return final_chunks
    
    def _split_by_semantic_boundaries(self, text: str) -> List[str]:
        """Split text by semantic boundaries (paragraphs, sections)."""
        # Split by double newlines (paragraphs)
        paragraphs = re.split(r'\n\n+', text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_length = len(para)
            
            # If adding this paragraph exceeds chunk size and we have content
            if current_length + para_length > self.chunk_size and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                
                # Start new chunk with overlap
                if self.chunk_overlap > 0 and len(current_chunk) > 1:
                    overlap_text = current_chunk[-1]
                    current_chunk = [overlap_text, para]
                    current_length = len(overlap_text) + para_length
                else:
                    current_chunk = [para]
                    current_length = para_length
            else:
                current_chunk.append(para)
                current_length += para_length
        
        # Add remaining chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def _split_by_size(self, text: str) -> List[str]:
        """Split text by fixed size with overlap."""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            
            # Try to find a sentence boundary near the end
            if end < text_length:
                # Look for sentence endings
                sentence_end = max(
                    text.rfind('.', start, end),
                    text.rfind('!', start, end),
                    text.rfind('?', start, end)
                )
                
                if sentence_end > start:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap if end < text_length else end
        
        return chunks
    
    def chunk_code(self, code: str) -> List[str]:
        """Chunk code while preserving logical structure."""
        # Split by function/class definitions
        pattern = r'(?=\n(?:def |class |async def ))'
        chunks = re.split(pattern, code)
        
        # Filter empty chunks
        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
        
        # If chunks are still too large, fall back to size-based splitting
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > self.chunk_size * 1.5:  # Allow larger chunks for code
                final_chunks.extend(self._split_by_size(chunk))
            else:
                final_chunks.append(chunk)
        
        return final_chunks