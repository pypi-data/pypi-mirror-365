"""In-memory cache implementation."""

import time
from typing import Any, Dict, Optional, Tuple

from .base import CacheManager


class LocalCacheManager(CacheManager):
    """Local in-memory cache using LRU."""

    def __init__(self, max_size: int = 10000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache if not expired."""
        if key in self._cache:
            value, expiry = self._cache[key]
            if expiry > time.time():
                self._hits += 1
                return value
            else:
                # Expired
                del self._cache[key]
        self._misses += 1
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value in cache with TTL."""
        if len(self._cache) >= self.max_size:
            # Simple eviction: remove oldest
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        expiry = time.time() + (ttl or self.default_ttl)
        self._cache[key] = (value, expiry)

    def delete(self, key: str) -> None:
        """Remove value from cache."""
        self._cache.pop(key, None)

    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        import fnmatch

        keys_to_delete = [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]
        for key in keys_to_delete:
            del self._cache[key]
        return len(keys_to_delete)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / (self._hits + self._misses) if (self._hits + self._misses) > 0 else 0,
            "size": len(self._cache),
            "max_size": self.max_size,
        }
