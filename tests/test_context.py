import pytest
from src.context.manager import ContextManager
from src.context.chunker import SemanticChunker


@pytest.mark.asyncio
async def test_context_indexing():
    """Test context indexing."""
    manager = ContextManager()
    
    await manager.index_content(
        documentation={
            "results": [
                {
                    "content": "This is a test documentation.",
                    "url": "https://example.com"
                }
            ]
        }
    )
    
    count = await manager.db.count()
    assert count > 0
    
    # Clean up
    await manager.clear()


def test_semantic_chunking():
    """Test semantic text chunking."""
    chunker = SemanticChunker(chunk_size=100, chunk_overlap=20)
    
    text = "This is paragraph one.\n\nThis is paragraph two.\n\nThis is paragraph three."
    
    chunks = chunker.chunk_text(text)
    
    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)