import sqlite3
import json
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class VectorDatabase:
    """SQLite-based vector database for context storage."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.database_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    embedding BLOB NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for faster searches
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at
                ON embeddings(created_at)
            """)
            
            conn.commit()
    
    async def insert(
        self,
        text: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Insert a text and its embedding."""
        embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
        metadata_json = json.dumps(metadata) if metadata else None
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO embeddings (text, embedding, metadata) VALUES (?, ?, ?)",
                (text, embedding_bytes, metadata_json)
            )
            conn.commit()
            return cursor.lastrowid
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar embeddings using cosine similarity."""
        query_vec = np.array(query_embedding, dtype=np.float32)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id, text, embedding, metadata FROM embeddings"
            )
            
            results = []
            for row in cursor:
                doc_id, text, embedding_bytes, metadata_json = row
                
                # Convert bytes back to numpy array
                embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_vec, embedding)
                
                metadata = json.loads(metadata_json) if metadata_json else {}
                
                results.append({
                    "id": doc_id,
                    "text": text,
                    "similarity": float(similarity),
                    "metadata": metadata
                })
            
            # Sort by similarity and return top_k
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:top_k]
    
    def _cosine_similarity(
        self,
        vec1: np.ndarray,
        vec2: np.ndarray
    ) -> float:
        """Calculate cosine similarity."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def clear(self) -> None:
        """Clear all embeddings."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM embeddings")
            conn.commit()
        
        logger.info("Database cleared")
    
    async def count(self) -> int:
        """Count total embeddings."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM embeddings")
            return cursor.fetchone()[0]