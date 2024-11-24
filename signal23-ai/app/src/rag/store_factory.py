from typing import Optional
from app.src.rag.store_base import VectorStoreBase
from app.src.rag.faiss_store import FAISSVectorStore
from app.src.rag.pg_store import PGVectorStore
from app.src.data.embeddings import get_embeddings_model
import os

class VectorStoreFactory:
    """
    Factory class to create appropriate vector store instance.
    Allows easy switching between FAISS and pgvector implementations.
    """
    
    @staticmethod
    def create_vector_store(store_type: Optional[str] = None) -> VectorStoreBase:
        """
        Create vector store instance based on configuration.
        
        Args:
            store_type: Optional override for store type
            
        Returns:
            VectorStoreBase: Configured vector store instance
        """
        embeddings = get_embeddings_model()
        
        # Use environment variable if store_type not specified
        if not store_type:
            store_type = os.getenv("VECTOR_STORE_TYPE", "faiss")
        
        if store_type.lower() == "pgvector":
            return PGVectorStore(embeddings)
        else:
            return FAISSVectorStore(embeddings)