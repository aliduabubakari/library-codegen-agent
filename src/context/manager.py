from typing import Dict, Any, List, Optional
import numpy as np

from .database import VectorDatabase
from .chunker import SemanticChunker
from .embeddings import EmbeddingService
from ..utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class ContextManager:
    """Manages context retrieval and optimization."""
    
    def __init__(self):
        self.db = VectorDatabase()
        self.chunker = SemanticChunker()
        self.embeddings = EmbeddingService()
        self.max_tokens = settings.max_context_tokens
    
    async def index_content(
        self,
        documentation: Optional[Dict[str, Any]] = None,
        github_info: Optional[Dict[str, Any]] = None,
        code_examples: Optional[List[str]] = None
    ) -> None:
        """Index all collected content."""
        logger.info("Indexing content")
        
        all_chunks = []
        
        # Process documentation
        if documentation:
            doc_chunks = await self._process_documentation(documentation)
            all_chunks.extend(doc_chunks)
        
        # Process GitHub info
        if github_info and github_info.get("readme"):
            readme_chunks = await self._process_readme(github_info["readme"])
            all_chunks.extend(readme_chunks)
        
        # Process code examples
        if code_examples:
            example_chunks = await self._process_examples(code_examples)
            all_chunks.extend(example_chunks)
        
        # Generate embeddings and store
        if all_chunks:
            await self._store_chunks(all_chunks)
        
        logger.info(f"Indexed {len(all_chunks)} chunks")
    
    async def _process_documentation(self, documentation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process and chunk documentation."""
        chunks = []
        
        results = documentation.get("results", [])
        for result in results:
            content = result.get("content", "")
            url = result.get("url", "")
            
            if content:
                doc_chunks = self.chunker.chunk_text(content)
                for chunk in doc_chunks:
                    chunks.append({
                        "text": chunk,
                        "source": url,
                        "type": "documentation"
                    })
        
        return chunks
    
    async def _process_readme(self, readme: str) -> List[Dict[str, Any]]:
        """Process and chunk README."""
        chunks = []
        
        readme_chunks = self.chunker.chunk_text(readme)
        for chunk in readme_chunks:
            chunks.append({
                "text": chunk,
                "source": "github_readme",
                "type": "readme"
            })
        
        return chunks
    
    async def _process_examples(self, examples: List[str]) -> List[Dict[str, Any]]:
        """Process code examples."""
        chunks = []
        
        for i, example in enumerate(examples):
            chunks.append({
                "text": example,
                "source": f"example_{i}",
                "type": "code_example"
            })
        
        return chunks
    
    async def _store_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """Generate embeddings and store chunks in database."""
        texts = [chunk["text"] for chunk in chunks]
        embeddings = await self.embeddings.embed_texts(texts)
        
        for chunk, embedding in zip(chunks, embeddings):
            await self.db.insert(
                text=chunk["text"],
                embedding=embedding,
                metadata={
                    "source": chunk["source"],
                    "type": chunk["type"]
                }
            )
    
    async def retrieve_relevant_context(
        self,
        query: str,
        library_name: str,
        top_k: int = None
    ) -> List[str]:
        """Retrieve most relevant context for a query."""
        if top_k is None:
            top_k = settings.top_k_results
        
        logger.info(f"Retrieving context for query: {query}")
        
        # Enhance query with library name
        enhanced_query = f"{library_name} {query}"
        
        # Generate query embedding
        query_embedding = await self.embeddings.embed_text(enhanced_query)
        
        # Search database
        results = await self.db.search(
            query_embedding=query_embedding,
            top_k=top_k * 2  # Get more initially for filtering
        )
        
        # Rank and filter results
        filtered_results = self._rank_and_filter(results, query)
        
        # Extract text, ensuring we don't exceed token limit
        context_texts = []
        total_tokens = 0
        
        for result in filtered_results[:top_k]:
            text = result["text"]
            tokens = self._estimate_tokens(text)
            
            if total_tokens + tokens <= self.max_tokens:
                context_texts.append(text)
                total_tokens += tokens
            else:
                break
        
        logger.info(f"Retrieved {len(context_texts)} context pieces ({total_tokens} tokens)")
        
        return context_texts
    
    def _rank_and_filter(
        self,
        results: List[Dict[str, Any]],
        query: str
    ) -> List[Dict[str, Any]]:
        """Rank and filter results based on relevance."""
        # Prioritize code examples if query mentions "example" or "how to"
        query_lower = query.lower()
        needs_examples = any(keyword in query_lower for keyword in ["example", "how to", "usage"])
        
        scored_results = []
        for result in results:
            score = result["similarity"]
            
            # Boost code examples if needed
            if needs_examples and result.get("metadata", {}).get("type") == "code_example":
                score *= 1.3
            
            scored_results.append({
                **result,
                "adjusted_score": score
            })
        
        # Sort by adjusted score
        scored_results.sort(key=lambda x: x["adjusted_score"], reverse=True)
        
        return scored_results
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)."""
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4
    
    async def clear(self) -> None:
        """Clear all indexed content."""
        await self.db.clear()