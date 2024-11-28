from typing import List, Tuple
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from app.src.rag.store_base import VectorStoreBase
import os

class FAISSVectorStore(VectorStoreBase):
    def __init__(self, embeddings_model):
        self.embeddings = embeddings_model
        self.index_name = "band_docs"
        self.store = self._load_or_create_store()
    
    def _load_or_create_store(self) -> FAISS:
        """Load existing store or create new one"""
        local_path = f"data/{self.index_name}"
        if os.path.exists(local_path):
            return FAISS.load_local(local_path, self.embeddings)
        return FAISS.from_documents([], self.embeddings)
    
    @classmethod
    def create(cls, embeddings_model, documents: List[Document] = None):
        """Create new store with optional documents"""
        store = cls(embeddings_model)
        if documents:
            store.add_documents(documents)
        return store
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to store"""
        if documents:
            self.store.add_documents(documents)
            self.save()
    
    def save(self):
        """Save store to disk"""
        os.makedirs("data", exist_ok=True)
        self.store.save_local(f"data/{self.index_name}")
    
    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        """Perform similarity search"""
        return self.store.similarity_search(query, k=k)
    
    def similarity_search_with_score(
        self, query: str, k: int = 3
    ) -> List[Tuple[Document, float]]:
        """Perform similarity search with scores"""
        return self.store.similarity_search_with_score(query, k=k)
    
    def delete_document(self, doc_id: str) -> None:
        """Delete document from store (not supported in FAISS)"""
        pass