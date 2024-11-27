from typing import List, Tuple
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from app.src.rag.store_base import VectorStoreBase
import os
from datetime import datetime
import boto3
import faiss
import numpy as np
import pickle

class FAISSVectorStore(VectorStoreBase):
    """
    FAISS implementation of vector store.
    Used in production for cost-effective storage.
    """
    
    def __init__(self, embeddings_model):
        self.embeddings = embeddings_model
        self.index_name = "band_docs"
        self.store = self._load_or_create_store()

    @classmethod
    def create(cls, embeddings_model, documents: List[Document] = None):
        """
        Create a new FAISS store with optional initial documents.
        
        Args:
            embeddings_model: The embeddings model to use
            documents: Optional list of documents to add initially
            
        Returns:
            FAISSVectorStore: The initialized vector store
        """
        store = cls(embeddings_model)
        if documents:
            store.add_documents(documents)
        return store
        
    def _load_or_create_store(self) -> FAISS:
        """
        Loads existing FAISS index or creates new one.
        Handles both local development and S3 production environments.
        
        Returns:
            FAISS: The loaded or created FAISS index
        """
        if os.getenv("ENVIRONMENT") == "production":
            return self._load_from_s3()
        else:
            local_path = f"data/{self.index_name}"
            if os.path.exists(local_path):
                return FAISS.load_local(local_path, self.embeddings)
            
            # Create empty store with proper dimensionality
            dimension = 384  # Default dimension for Mistral embeddings
            try:
                # Try to get actual dimension from embeddings model
                sample_embedding = self.embeddings.embed_query("test")
                dimension = len(sample_embedding)
            except:
                pass
                
            # Create empty texts list and embeddings matrix
            texts = []
            embeddings = np.array([], dtype=np.float32).reshape(0, dimension)
            
            # Initialize FAISS index
            index = faiss.IndexFlatL2(dimension)
            
            # Create and return empty store
            return FAISS(
                embeddings=self.embeddings,
                index=index,
                docstore=FAISS.DocStore(),
                index_to_docstore_id={}
            )
            
    def _load_from_s3(self) -> FAISS:
        """
        Loads FAISS index from S3 in production environment.
        
        Returns:
            FAISS: The loaded FAISS index
        
        Raises:
            Exception: If S3 load fails
        """
        try:
            s3 = boto3.client('s3')
            bucket = os.getenv("S3_BUCKET")
            
            # Download index files
            s3.download_file(bucket, f"{self.index_name}.faiss", "index.faiss")
            s3.download_file(bucket, f"{self.index_name}.pkl", "index.pkl")
            
            # Load FAISS index
            store = FAISS.load_local(".", self.embeddings)
            
            # Cleanup temporary files
            os.remove("index.faiss")
            os.remove("index.pkl")
            
            return store
        except Exception as e:
            print(f"Error loading from S3: {e}")
            dimension = 384  # Default dimension for Mistral embeddings
            try:
                sample_embedding = self.embeddings.embed_query("test")
                dimension = len(sample_embedding)
            except:
                pass
            
            index = faiss.IndexFlatL2(dimension)
            return FAISS(
                embeddings=self.embeddings,
                index=index,
                docstore=FAISS.DocStore(),
                index_to_docstore_id={}
            )

    def save(self):
        """
        Saves the FAISS index either locally or to S3.
        """
        if os.getenv("ENVIRONMENT") == "production":
            self._save_to_s3()
        else:
            os.makedirs("data", exist_ok=True)
            self.store.save_local(f"data/{self.index_name}")
            
    def _save_to_s3(self):
        """
        Saves FAISS index to S3 in production environment.
        """
        try:
            # Save temporarily
            self.store.save_local(".")
            
            # Upload to S3
            s3 = boto3.client('s3')
            bucket = os.getenv("S3_BUCKET")
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            
            s3.upload_file("index.faiss", bucket, f"{self.index_name}.faiss")
            s3.upload_file("index.pkl", bucket, f"{self.index_name}.pkl")
            
            # Backup existing index
            s3.copy_object(
                Bucket=bucket,
                CopySource=f"{bucket}/{self.index_name}.faiss",
                Key=f"backups/{self.index_name}_{timestamp}.faiss"
            )
            
            # Cleanup
            os.remove("index.faiss")
            os.remove("index.pkl")
        except Exception as e:
            print(f"Error saving to S3: {e}")

    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        """
        Perform similarity search in FAISS.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List[Document]: Similar documents
        """
        return self.store.similarity_search(query, k=k)
    
    def similarity_search_with_score(
        self, query: str, k: int = 3
    ) -> List[Tuple[Document, float]]:
        """
        Perform similarity search with scores in FAISS.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List[Tuple[Document, float]]: Documents with similarity scores
        """
        return self.store.similarity_search_with_score(query, k=k)
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to FAISS store.
        
        Args:
            documents: Documents to add
        """
        self.store.add_documents(documents)
        self.save()
    
    def delete_document(self, doc_id: str) -> None:
        """
        Delete document from FAISS store.
        
        Args:
            doc_id: ID of document to delete
        """
        # FAISS doesn't support document deletion directly
        # You would need to rebuild the index without the document
        # This is a placeholder implementation
        pass