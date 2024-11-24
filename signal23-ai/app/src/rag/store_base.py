from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document

class VectorStoreBase(ABC):
    """
    Abstract base class for vector stores.
    Defines the interface that both FAISS and pgvector implementations must follow.
    """
    
    @abstractmethod
    async def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        """Perform similarity search"""
        pass
    
    @abstractmethod
    async def similarity_search_with_score(
        self, query: str, k: int = 3
    ) -> List[Tuple[Document, float]]:
        """Perform similarity search with relevance scores"""
        pass
    
    @abstractmethod
    async def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the store"""
        pass
    
    @abstractmethod
    async def delete_document(self, doc_id: str) -> None:
        """Delete a document from the store"""
        pass