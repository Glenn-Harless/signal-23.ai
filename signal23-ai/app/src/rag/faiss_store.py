from typing import List, Tuple
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from app.src.rag.store_base import VectorStoreBase
import os
from datetime import datetime
import boto3

class FAISSVectorStore(VectorStoreBase):
    """
    FAISS implementation of vector store.
    Used in production for cost-effective storage.
    """
    
    def __init__(self, embeddings_model):
        self.embeddings = embeddings_model
        self.index_name = "band_docs"
        self.store = self._load_or_create_store()
        
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
            return FAISS.from_documents([], self.embeddings)
            
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
            return FAISS.from_documents([], self.embeddings)

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