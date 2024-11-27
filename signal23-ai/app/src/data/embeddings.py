from typing import List, Optional, Dict
import numpy as np
from langchain_ollama import OllamaEmbeddings
from pydantic import BaseModel
import logging
import hashlib
import json
from pathlib import Path
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class EmbeddingMetadata(BaseModel):
    """Metadata for embedding vectors"""
    model: str
    dimension: int
    created_at: str
    content_hash: str

class EmbeddingCache(BaseModel):
    """Cache structure for embeddings"""
    metadata: EmbeddingMetadata
    vectors: Dict[str, List[float]]

class EnhancedEmbeddingsGenerator:
    """Enhanced embeddings generator with caching and batch processing"""
    
    def __init__(
        self,
        model_name: str = "mistral",
        cache_dir: str = "data/embeddings_cache",
        batch_size: int = 10,
        dimension: int = 384  # Mistral's default embedding dimension
    ):
        self.model_name = model_name
        self.cache_dir = Path(cache_dir)
        self.batch_size = batch_size
        self.dimension = dimension
        
        self.embeddings = OllamaEmbeddings(
            # base_url="http://ollama:11434", # docker
            base_url="http://localhost:11434", # local
            model=model_name
        )
        
        # Initialize cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        try:
            print(f"Generating embeddings using Ollama at {self.embeddings.base_url}")
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            raise
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise

    def _get_content_hash(self, text: str) -> str:
        """Generate hash for text content"""
        return hashlib.sha256(text.encode()).hexdigest()

    def _process_batch(
        self,
        batch: List[str],
        cache: Dict[str, List[float]],
        use_cache: bool
    ) -> List[List[float]]:
        """Process a batch of texts"""
        batch_embeddings = []
        texts_to_embed = []
        cache_indices = []

        # Check cache first
        for idx, text in enumerate(batch):
            content_hash = self._get_content_hash(text)
            if use_cache and content_hash in cache:
                batch_embeddings.append(cache[content_hash])
            else:
                texts_to_embed.append(text)
                cache_indices.append(idx)

        # Generate new embeddings for cache misses
        if texts_to_embed:
            # Use embed_documents instead of aembed_documents
            new_embeddings = self.embeddings.embed_documents(texts_to_embed)
            
            # Update cache with new embeddings
            for text, embedding in zip(texts_to_embed, new_embeddings):
                content_hash = self._get_content_hash(text)
                cache[content_hash] = embedding

            # Insert new embeddings in correct positions
            for cache_idx, embedding in zip(cache_indices, new_embeddings):
                batch_embeddings.insert(cache_idx, embedding)

        return batch_embeddings

    def _get_cache_path(self) -> Path:
        """Get path to cache file"""
        return self.cache_dir / f"embeddings_cache_{self.model_name}.json"

    def _load_cache(self) -> Dict[str, List[float]]:
        """Load embedding cache from disk"""
        cache_path = self._get_cache_path()
        if not cache_path.exists():
            return {}

        try:
            with open(cache_path, 'r') as f:
                cache_data = EmbeddingCache.parse_raw(f.read())
                
            # Validate cache metadata
            if (cache_data.metadata.model != self.model_name or
                cache_data.metadata.dimension != self.dimension):
                logger.warning("Cache metadata mismatch, clearing cache")
                return {}
                
            return cache_data.vectors
        except Exception as e:
            logger.error(f"Error loading cache: {str(e)}")
            return {}

    def _save_cache(self, cache: Dict[str, List[float]]):
        """Save embedding cache to disk"""
        try:
            cache_data = EmbeddingCache(
                metadata=EmbeddingMetadata(
                    model=self.model_name,
                    dimension=self.dimension,
                    created_at=datetime.now().isoformat(),
                    content_hash=hashlib.sha256(
                        json.dumps(cache).encode()
                    ).hexdigest()
                ),
                vectors=cache
            )
            
            with open(self._get_cache_path(), 'w') as f:
                f.write(cache_data.json())
                
        except Exception as e:
            logger.error(f"Error saving cache: {str(e)}")

    def similarity_search(
        self,
        query: str,
        documents: List[str],
        top_k: int = 3
    ) -> List[tuple[int, float]]:
        """
        Perform similarity search between query and documents.
        """
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Generate document embeddings
        doc_embeddings = self.generate_embeddings(documents)
        
        # Calculate similarities
        similarities = []
        for idx, doc_embedding in enumerate(doc_embeddings):
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append((idx, similarity))
        
        # Sort by similarity and return top_k
        return sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        v1_arr = np.array(v1)
        v2_arr = np.array(v2)
        return np.dot(v1_arr, v2_arr) / (
            np.linalg.norm(v1_arr) * np.linalg.norm(v2_arr)
        )
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Alias for generate_embeddings for compatibility with LangChain interface
        """
        return self.generate_embeddings(texts)

# Create a singleton instance for global use
_embeddings_generator: Optional[EnhancedEmbeddingsGenerator] = None

def get_embeddings_model(
    model_name: str = "mistral",
    force_new: bool = False
) -> EnhancedEmbeddingsGenerator:
    """
    Get or create embeddings generator instance.
    """
    global _embeddings_generator
    
    if _embeddings_generator is None or force_new:
        _embeddings_generator = EnhancedEmbeddingsGenerator(
            model_name=model_name,
            cache_dir=os.getenv("EMBEDDINGS_CACHE_DIR", "data/embeddings_cache"),
            batch_size=int(os.getenv("EMBEDDINGS_BATCH_SIZE", "10"))
        )
    
    return _embeddings_generator