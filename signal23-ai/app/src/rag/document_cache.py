# app/src/rag/document_cache.py
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import json
from pathlib import Path
import logging
import asyncio
import hashlib
from collections import OrderedDict
import os

logger = logging.getLogger(__name__)

class CacheMetadata(BaseModel):
    """Metadata for cached documents"""
    last_accessed: datetime
    expires_at: Optional[datetime]
    source: str
    version: str
    content_hash: str

class CachedDocument(BaseModel):
    """Structure for cached document with metadata"""
    content: str
    metadata: CacheMetadata
    embedding_id: Optional[str] = None

class DocumentCache:
    """
    LRU cache implementation for document storage with disk persistence.
    Handles document caching, cleanup, and version management.
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        ttl_days: int = 7,
        cache_dir: str = "data/document_cache",
        cleanup_interval: int = 3600  # 1 hour
    ):
        self.max_size = max_size
        self.ttl = timedelta(days=ttl_days)
        self.cache_dir = Path(cache_dir)
        self.cleanup_interval = cleanup_interval
        
        # Initialize cache storage
        self.cache: OrderedDict[str, CachedDocument] = OrderedDict()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing cache from disk
        self._load_cache()
        
        # Start cleanup task
        asyncio.create_task(self._periodic_cleanup())
    
    async def get(self, key: str) -> Optional[CachedDocument]:
        """
        Retrieve document from cache.
        Updates last accessed time and handles cache misses.
        """
        try:
            if key in self.cache:
                document = self.cache.pop(key)  # Remove and re-add for LRU
                
                # Check if document has expired
                if document.metadata.expires_at and \
                   document.metadata.expires_at <= datetime.utcnow():
                    await self.remove(key)
                    return None
                
                # Update last accessed time
                document.metadata.last_accessed = datetime.utcnow()
                self.cache[key] = document  # Re-add to end
                return document
                
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving from cache: {str(e)}")
            return None

    async def put(
        self,
        key: str,
        content: str,
        source: str,
        version: str = "1.0",
        ttl_days: Optional[int] = None
    ) -> None:
        """
        Add document to cache with metadata.
        Handles cache size limits and disk persistence.
        """
        try:
            # Calculate content hash
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # Create cache entry
            document = CachedDocument(
                content=content,
                metadata=CacheMetadata(
                    last_accessed=datetime.utcnow(),
                    expires_at=datetime.utcnow() + timedelta(days=ttl_days or self.ttl.days),
                    source=source,
                    version=version,
                    content_hash=content_hash
                )
            )
            
            # Remove oldest item if cache is full
            if len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
            
            # Add new document
            self.cache[key] = document
            
            # Save to disk
            await self._save_to_disk(key, document)
            
        except Exception as e:
            logger.error(f"Error adding to cache: {str(e)}")

    async def remove(self, key: str) -> None:
        """Remove document from cache and disk"""
        try:
            if key in self.cache:
                del self.cache[key]
                
            # Remove from disk
            cache_file = self.cache_dir / f"{key}.json"
            if cache_file.exists():
                cache_file.unlink()
                
        except Exception as e:
            logger.error(f"Error removing from cache: {str(e)}")

    async def clear(self) -> None:
        """Clear entire cache and remove all cache files"""
        try:
            self.cache.clear()
            
            # Remove all cache files
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")

    async def _periodic_cleanup(self):
        """Periodic task to clean expired cache entries"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_expired()
                await self._cleanup_oversized()
            except Exception as e:
                logger.error(f"Error in cleanup task: {str(e)}")

    async def _cleanup_expired(self):
        """Remove expired cache entries"""
        now = datetime.utcnow()
        expired_keys = [
            key for key, doc in self.cache.items()
            if doc.metadata.expires_at and doc.metadata.expires_at <= now
        ]
        
        for key in expired_keys:
            await self.remove(key)

    async def _cleanup_oversized(self):
        """Remove oldest entries if cache exceeds max size"""
        while len(self.cache) > self.max_size:
            self.cache.popitem(last=False)

    def _load_cache(self):
        """Load cache from disk on startup"""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                with open(cache_file, 'r') as f:
                    key = cache_file.stem
                    document = CachedDocument.parse_raw(f.read())
                    self.cache[key] = document
        except Exception as e:
            logger.error(f"Error loading cache from disk: {str(e)}")

    async def _save_to_disk(self, key: str, document: CachedDocument):
        """Save cache entry to disk"""
        try:
            cache_file = self.cache_dir / f"{key}.json"
            with open(cache_file, 'w') as f:
                f.write(document.json())
        except Exception as e:
            logger.error(f"Error saving cache to disk: {str(e)}")

# Create global cache instance
_document_cache: Optional[DocumentCache] = None

def get_document_cache(
    force_new: bool = False,
    **kwargs
) -> DocumentCache:
    """Get or create document cache instance"""
    global _document_cache
    
    if _document_cache is None or force_new:
        _document_cache = DocumentCache(
            max_size=int(os.getenv("DOCUMENT_CACHE_SIZE", "1000")),
            ttl_days=int(os.getenv("DOCUMENT_CACHE_TTL", "7")),
            cache_dir=os.getenv("DOCUMENT_CACHE_DIR", "data/document_cache"),
            cleanup_interval=int(os.getenv("CACHE_CLEANUP_INTERVAL", "3600")),
            **kwargs
        )
    
    return _document_cache