from typing_extensions import Protocol, Any, runtime_checkable


@runtime_checkable
class CacheProtocol(Protocol):
    """
    Defines the required interface for all cache implementations
    in the application (e.g., BasicCache, RedisCache).
    """

    def get(self, key: Any) -> Any | None:
        """Return value for key, or None if missing/expired."""
        ...  # Implementation details are ignored in the Protocol

    def put(self, key: Any, value: Any, ttl_seconds: int | None = None):
        """Insert or update key with value."""
        ...

    def delete(self, key: Any) -> bool:
        """Delete key if present. Returns True if removed."""
        ...

    def clear(self):
        """Clear cache."""
        ...

    def decorator(self, ttl_seconds: int | None = None):
        """Return a decorator that caches function results."""
        ...
