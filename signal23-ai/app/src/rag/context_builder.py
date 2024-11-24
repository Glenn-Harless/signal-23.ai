from typing import List, Dict, Any
from langchain_core.documents import Document

class ContextBuilder:
    """
    Builds context strings from retrieved documents for the LLM.
    Handles formatting and relevance scoring of context information.
    """
    
    @staticmethod
    def build_context(documents: List[Document], scores: List[float]) -> str:
        """
        Builds a formatted context string from retrieved documents.
        
        Args:
            documents: List of retrieved documents
            scores: Relevance scores for each document
            
        Returns:
            str: Formatted context string for LLM
        """
        if not documents:
            return "No relevant context available."
            
        context_parts = []
        for doc, score in zip(documents, scores):
            context_parts.append(
                f"[Source: {doc.metadata.get('title', 'Unknown')} "
                f"(Relevance: {score:.2f})]\n{doc.page_content}"
            )
            
        return "\n\n".join(context_parts)