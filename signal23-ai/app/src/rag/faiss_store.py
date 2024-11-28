from typing import List, Tuple
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from app.src.rag.store_base import VectorStoreBase
import os
from pathlib import Path

class FAISSVectorStore(VectorStoreBase):
    def __init__(self, embeddings_model):
        self.embeddings = embeddings_model
        self.index_name = "band_docs"
        self.store = self._load_or_create_store()

    def _load_or_create_store(self) -> FAISS:
        """Load existing store or create empty one"""
        store_path = Path(f"data/{self.index_name}")
        if store_path.exists() and (store_path / "index.faiss").exists():
            # Load existing store with safety flag
            return FAISS.load_local(
                str(store_path), 
                self.embeddings,
                allow_dangerous_deserialization=True  # Only for trusted local files
            )
        return None

    @classmethod
    def create(cls, embeddings_model, documents: List[Document] = None):
        """Create new store with initial documents"""
        instance = cls(embeddings_model)
        
        if documents:
            # Create store with provided documents
            instance.store = FAISS.from_documents(documents, embeddings_model)
        else:
            # Create store by getting dimension from a test embedding
            sample_embedding = embeddings_model.embed_query("test")
            texts = ["test"]
            metadatas = [{"source": "test"}]
            instance.store = FAISS.from_texts(texts, embeddings_model, metadatas=metadatas)
            # Remove the test document
            instance.store.delete(["0"])
            
        return instance
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to store"""
        if not self.store:
            self.store = FAISS.from_documents(documents, self.embeddings)
        else:
            self.store.add_documents(documents)
        self.save()
    
    def save(self):
        """Save store to disk"""
        if self.store:
            os.makedirs("data", exist_ok=True)
            self.store.save_local(f"data/{self.index_name}")
    
    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        """Perform similarity search"""
        if not self.store:
            return []
        return self.store.similarity_search(query, k=k)
    
    def similarity_search_with_score(
        self, query: str, k: int = 3
    ) -> List[Tuple[Document, float]]:
        """Perform similarity search with scores"""
        if not self.store:
            return []
        return self.store.similarity_search_with_score(query, k=k)
    
    def delete_document(self, doc_id: str) -> None:
        """Delete document from store"""
        if self.store:
            self.store.delete([doc_id])