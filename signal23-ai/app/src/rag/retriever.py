from typing import List, Dict, Any, Optional
from app.src.rag.store_factory import VectorStoreFactory

class DocumentRetriever:
    """
    Handles document retrieval using configured vector store.
    Works with both FAISS and pgvector implementations.
    """
    
    def __init__(self, store_type: Optional[str] = None):
        """
        Initialize retriever with specified store type.
        
        Args:
            store_type: Optional override for store type
        """
        self.store = VectorStoreFactory.create_vector_store(store_type)
    
    async def get_relevant_context(self, query: str, k: int = 3) -> str:
        """
        Retrieves relevant context for a query.
        
        Args:
            query: The user's question
            k: Number of relevant documents to retrieve
            
        Returns:
            str: Formatted context from relevant documents
        """
        docs_with_scores = await self.store.similarity_search_with_score(query, k=k)
        
        if not docs_with_scores:
            return "No relevant context found."
            
        context_parts = []
        for doc, score in docs_with_scores:
            context_parts.append(
                f"[Relevance: {score:.2f}] {doc.page_content}"
            )
            
        return "\n\n".join(context_parts)
        
    def get_sources(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Gets source information for citations.
        
        Args:
            query: The user's question
            k: Number of sources to retrieve
            
        Returns:
            List[Dict]: Source documents with metadata
        """
        docs_with_scores = self.store.store.similarity_search_with_score(query, k=k)
        
        return [
            {
                "title": doc.metadata.get("title", "Unknown"),
                "content": doc.page_content,
                "confidence": float(score)
            }
            for doc, score in docs_with_scores
        ]

# Global retriever instance
_retriever_instance: Optional[DocumentRetriever] = None

async def get_relevant_context(query: str, k: int = 3) -> str:
    """
    Helper function to get relevant context for a query.
    Uses a singleton instance of DocumentRetriever.
    
    Args:
        query: The user's question
        k: Number of relevant documents to retrieve
        
    Returns:
        str: Formatted context from relevant documents
    """
    global _retriever_instance
    
    if _retriever_instance is None:
        _retriever_instance = DocumentRetriever()
        
    return await _retriever_instance.get_relevant_context(query, k)