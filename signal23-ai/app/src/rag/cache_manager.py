# app/src/rag/cache_manager.py
from typing import Dict, List, Optional, Union
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging
import asyncio
from pathlib import Path
import shutil
import json

logger = logging.getLogger(__name__)

class CacheStats(BaseModel):
    """Statistics about cache usage"""
    total_entries: int
    total_size_bytes: int
    hit_rate: float
    miss_rate: float
    avg_access_time_ms: float
    oldest_entry: Optional[datetime]
    newest_entry: Optional[datetime]

class CacheManager:
    """
    Manages cache operations, cleanup, and monitoring across different cache types.
    Handles both document and embedding caches.
    """
    
    def __init__(
        self,
        document_cache_dir: str = "data/document_cache",
        embedding_cache_dir: str = "data/embeddings_cache",
        max_cache_size_mb: int = 1000,
        stats_update_interval: int = 300  # 5 minutes
    ):
        self.document_cache_dir = Path(document_cache_dir)
        self.embedding_cache_dir = Path(embedding_cache_dir)
        self.max_cache_size_mb = max_cache_size_mb
        self.stats_update_interval = stats_update_interval
        
        # Performance metrics
        self.cache_hits = 0
        self.cache_misses = 0
        self.access_times: List[float] = []
        
        # Start stats collection
        asyncio.create_task(self._collect_stats())
    
    async def get_cache_stats(self) -> Dict[str, CacheStats]:
        """Get statistics for all cache types"""
        return {
            "document_cache": await self._get_cache_stats(self.document_cache_dir),
            "embedding_cache": await self._get_cache_stats(self.embedding_cache_dir)
        }
    
    async def cleanup_caches(
        self,
        older_than_days: Optional[int] = None,
        target_size_mb: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Clean up cache directories based on age or size targets.
        Returns number of entries removed from each cache.
        """
        cleanup_stats = {
            "document_cache": await self._cleanup_cache(
                self.document_cache_dir, older_than_days, target_size_mb
            ),
            "embedding_cache": await self._cleanup_cache(
                self.embedding_cache_dir, older_than_days, target_size_mb
            )
        }
        
        logger.info(f"Cache cleanup completed: {cleanup_stats}")
        return cleanup_stats
    
    async def optimize_caches(self) -> Dict[str, Any]:
        """
        Optimize cache storage and performance.
        Consolidates fragmented cache files and updates indices.
        """
        optimization_results = {
            "document_cache": await self._optimize_cache(self.document_cache_dir),
            "embedding_cache": await self._optimize_cache(self.embedding_cache_dir)
        }
        
        logger.info(f"Cache optimization completed: {optimization_results}")
        return optimization_results
    
    async def _get_cache_stats(self, cache_dir: Path) -> CacheStats:
        """Calculate statistics for a cache directory"""
        try:
            total_size = sum(f.stat().st_size for f in cache_dir.glob("**/*"))
            entries = list(cache_dir.glob("*.json"))
            
            if not entries:
                return CacheStats(
                    total_entries=0,
                    total_size_bytes=0,
                    hit_rate=0.0,
                    miss_rate=0.0,
                    avg_access_time_ms=0.0,
                    oldest_entry=None,
                    newest_entry=None
                )
            
            # Calculate dates
            dates = [datetime.fromtimestamp(f.stat().st_mtime) for f in entries]
            
            total_requests = self.cache_hits + self.cache_misses
            hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0
            
            return CacheStats(
                total_entries=len(entries),
                total_size_bytes=total_size,
                hit_rate=hit_rate,
                miss_rate=1 - hit_rate,
                avg_access_time_ms=sum(self.access_times) / len(self.access_times) 
                    if self.access_times else 0,
                oldest_entry=min(dates) if dates else None,
                newest_entry=max(dates) if dates else None
            )
            
        except Exception as e:
            logger.error(f"Error calculating cache stats: {str(e)}")
            return CacheStats(
                total_entries=0,
                total_size_bytes=0,
                hit_rate=0.0,
                miss_rate=0.0,
                avg_access_time_ms=0.0,
                oldest_entry=None,
                newest_entry=None
            )
    
    async def _cleanup_cache(
        self,
        cache_dir: Path,
        older_than_days: Optional[int],
        target_size_mb: Optional[int]
    ) -> int:
        """Clean up a specific cache directory"""
        removed_count = 0
        try:
            # Age-based cleanup
            if older_than_days is not None:
                cutoff = datetime.now() - timedelta(days=older_than_days)
                for cache_file in cache_dir.glob("*.json"):
                    if datetime.fromtimestamp(cache_file.stat().st_mtime) < cutoff:
                        cache_file.unlink()
                        removed_count += 1
            
            # Size-based cleanup
            if target_size_mb is not None:
                target_bytes = target_size_mb * 1024 * 1024
                current_size = sum(f.stat().st_size for f in cache_dir.glob("**/*"))
                
                if current_size > target_bytes:
                    # Remove oldest files first
                    files = sorted(
                        cache_dir.glob("*.json"),
                        key=lambda x: x.stat().st_mtime
                    )
                    
                    while current_size > target_bytes and files:
                        file_to_remove = files.pop(0)
                        current_size -= file_to_remove.stat().st_size
                        file_to_remove.unlink()
                        removed_count += 1
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Error cleaning up cache: {str(e)}")
            return removed_count

    async def _optimize_cache(self, cache_dir: Path) -> Dict[str, Any]:
            """Optimize a specific cache directory"""
            try:
                # Create temporary optimization directory
                temp_dir = cache_dir.parent / f"{cache_dir.name}_temp"
                temp_dir.mkdir(exist_ok=True)
                
                # Track optimization metrics
                stats = {
                    'files_processed': 0,
                    'size_before': 0,
                    'size_after': 0,
                    'corrupted_files': 0,
                    'duplicate_data': 0
                }
                
                # Track unique content hashes to detect duplicates
                content_hashes = set()
                
                # Process cache files
                for cache_file in cache_dir.glob("*.json"):
                    try:
                        stats['size_before'] += cache_file.stat().st_size
                        
                        with open(cache_file, 'r') as f:
                            data = json.load(f)
                            
                        # Check for duplicate content
                        content_hash = hashlib.sha256(
                            json.dumps(data, sort_keys=True).encode()
                        ).hexdigest()
                        
                        if content_hash in content_hashes:
                            stats['duplicate_data'] += 1
                            continue
                            
                        content_hashes.add(content_hash)
                        
                        # Optimize and write to temp directory
                        optimized_path = temp_dir / cache_file.name
                        with open(optimized_path, 'w') as f:
                            json.dump(data, f, separators=(',', ':'))
                            
                        stats['files_processed'] += 1
                        stats['size_after'] += optimized_path.stat().st_size
                        
                    except json.JSONDecodeError:
                        stats['corrupted_files'] += 1
                        logger.warning(f"Corrupted cache file found: {cache_file}")
                        continue
                    except Exception as e:
                        logger.error(f"Error processing file {cache_file}: {str(e)}")
                        continue

                # Replace old cache with optimized version
                shutil.rmtree(cache_dir)
                temp_dir.rename(cache_dir)
                
                # Create optimization report
                stats['space_saved'] = stats['size_before'] - stats['size_after']
                stats['space_saved_percentage'] = (
                    (stats['space_saved'] / stats['size_before']) * 100 
                    if stats['size_before'] > 0 else 0
                )
                
                logger.info(f"Cache optimization completed: {stats}")
                return stats
                
            except Exception as e:
                logger.error(f"Error optimizing cache: {str(e)}")
                return {
                    'error': str(e),
                    'files_processed': 0,
                    'space_saved': 0
                }

    async def _collect_stats(self):
        """Periodic task to collect cache statistics"""
        while True:
            try:
                await asyncio.sleep(self.stats_update_interval)
                stats = await self.get_cache_stats()
                
                # Reset performance metrics after collection
                self.access_times = self.access_times[-1000:]  # Keep last 1000 samples
                
                # Log cache health metrics
                for cache_type, cache_stats in stats.items():
                    if cache_stats.total_size_bytes > (self.max_cache_size_mb * 1024 * 1024):
                        logger.warning(
                            f"{cache_type} exceeds size limit. Current: "
                            f"{cache_stats.total_size_bytes // (1024*1024)}MB, "
                            f"Limit: {self.max_cache_size_mb}MB"
                        )
                    
                    if cache_stats.hit_rate < 0.5:
                        logger.warning(
                            f"Low hit rate for {cache_type}: {cache_stats.hit_rate:.2%}"
                        )
                        
            except Exception as e:
                logger.error(f"Error collecting cache stats: {str(e)}")