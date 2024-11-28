from typing import List, Optional
from langchain_core.embeddings import Embeddings
from langchain_ollama import OllamaEmbeddings
import logging
import os
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class CachedEmbeddings(Embeddings):
    """
    A LangChain-compatible embeddings class with caching support.
    Implements the standard LangChain Embeddings interface.
    """
    
    def __init__(
        self,
        model_name: str = "mistral",
        cache_dir: str = "data/embeddings_cache",
    ):
        self.model_name = model_name
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        print(f"Initializing Ollama with base_url: {base_url}")

        
        # Initialize underlying Ollama embeddings
        self.ollama = OllamaEmbeddings(
            model=model_name,
            base_url=base_url
        )
        # Load cache if it exists
        self.cache = self._load_cache()
    
    def _get_cache_path(self) -> Path:
        """Get path to cache file"""
        return self.cache_dir / f"embeddings_cache_{self.model_name}.json"
    
    def _load_cache(self) -> dict:
        """Load cache from disk"""
        cache_path = self._get_cache_path()
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading cache: {e}")
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to disk"""
        try:
            with open(self._get_cache_path(), 'w') as f:
                json.dump(self.cache, f)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents.
        This method matches LangChain's Embeddings interface.
        """
        results = []
        texts_to_embed = []
        cached_indices = {}
        
        # Check cache first
        for i, text in enumerate(texts):
            if text in self.cache:
                results.append(self.cache[text])
            else:
                texts_to_embed.append(text)
                cached_indices[len(texts_to_embed) - 1] = i
        
        # Generate new embeddings for cache misses
        if texts_to_embed:
            print(f"Generating embeddings for {len(texts_to_embed)} texts")
            new_embeddings = self.ollama.embed_documents(texts_to_embed)
            
            # Update cache with new embeddings
            for text, embedding in zip(texts_to_embed, new_embeddings):
                self.cache[text] = embedding
            
            # Save updated cache
            self._save_cache()
            
            # Insert new embeddings into results
            for i, embedding in enumerate(new_embeddings):
                orig_idx = cached_indices[i]
                while len(results) <= orig_idx:
                    results.append(None)
                results[orig_idx] = embedding
        
        return results
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query.
        This method matches LangChain's Embeddings interface.
        """
        if text in self.cache:
            return self.cache[text]
        
        embedding = self.ollama.embed_query(text)
        self.cache[text] = embedding
        self._save_cache()
        
        return embedding

# Singleton instance for global use
_embeddings_instance: Optional[CachedEmbeddings] = None

def get_embeddings_model(
    model_name: str = "mistral",
    force_new: bool = False
) -> CachedEmbeddings:
    """Get or create embeddings instance"""
    global _embeddings_instance
    
    if _embeddings_instance is None or force_new:
        _embeddings_instance = CachedEmbeddings(
            model_name=model_name,
            cache_dir=os.getenv("EMBEDDINGS_CACHE_DIR", "data/embeddings_cache"),
        )
    
    return _embeddings_instance