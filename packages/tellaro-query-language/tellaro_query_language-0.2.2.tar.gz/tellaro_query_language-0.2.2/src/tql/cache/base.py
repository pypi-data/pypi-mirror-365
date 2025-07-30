"""Base cache infrastructure."""

from typing import Any, Dict, Optional


class CacheManager:
    """Base class for cache management."""

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value in cache."""

    def delete(self, key: str) -> None:
        """Remove value from cache."""

    def clear_pattern(self, pattern: str) -> int:  # pylint: disable=unused-argument
        """Clear all keys matching pattern."""
        return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {}
