import threading
import time

from typing_extensions import Any, Callable

from app.core.caching.cache_protocols import CacheProtocol

# --- Helper Class: Node ---


class _Node:
    """
    Represents a single entry in the cache.
    It stores the key, the actual value, and the Unix timestamp
    when the entry should expire (Time-To-Live).
    """

    __slots__ = ("key", "value", "expiry")

    def __init__(self, key=None, value=None, expiry: float | None = None):
        self.key = key
        self.value = value
        # Unix timestamp when the item should expire (seconds since epoch)
        self.expiry = expiry


class OrderDictCache(CacheProtocol):
    """
    Implements a thread-safe, fixed-capacity, LRU (Least Recently Used) cache
    with optional TTL (Time-To-Live) support for each entry.

    It uses a standard Python dictionary (available in Python 3.7+ onwards)
    to achieve ordered insertion and efficient LRU eviction, treating the
    dictionary's start as the LRU position and the end as the MRU position.

    Attributes:
        capacity (int): The maximum number of items the cache can hold.
        ttl (int | None): The default expiry time in seconds for new entries.
        map (dict): The underlying dictionary storing {_Node} objects.
        lock (threading.Lock | None): Used for thread-safe access to the cache.
    """

    def __init__(
        self,
        capacity: int,
        ttl_seconds: int | None = None,
        thread_safe: bool = False,
    ):
        if capacity <= 0:
            raise ValueError("capacity must be > 0")

        self.capacity = int(capacity)
        self.ttl = ttl_seconds

        self.map = {}

        self.lock = threading.Lock() if thread_safe else None

    def _now(self) -> float:
        """Returns the current Unix timestamp."""
        return time.time()

    def _is_expired(self, node: _Node) -> bool:
        """Checks if a node has passed its expiry time."""
        if node.expiry is None:
            return False
        return self._now() >= node.expiry

    def __len__(self):
        """Returns the current number of items in the cache (map length)."""
        return len(self.map)

    def _get(self, key: Any) -> Any | None:
        """Return value for key, or None if missing/expired."""
        if key not in self.map:
            return None

        node = self.map.get(key)

        if self._is_expired(node):
            del self.map[key]
            return None

        # remove the value and then put the value at the end (MRU position).
        self.map.pop(key)
        self.map[key] = node

        return node.value

    def get(self, key: Any) -> Any | None:
        if self.lock:
            with self.lock:
                return self._get(key)
        else:
            return self._get(key)

    def _put(self, key: Any, value: Any, ttl_seconds: int | None = None):
        """Insert or update key with value."""
        node = self.map.get(key)
        expiry = None

        effective_ttl = self.ttl if ttl_seconds is None else ttl_seconds
        if effective_ttl is not None:
            expiry = self._now() + effective_ttl

        if node:
            node.value = value
            node.expiry = expiry
            self.map.pop(key)
            self.map[key] = node
            return

        new_node = _Node(key, value, expiry)

        if len(self.map) >= self.capacity:
            self.map.popitem(last=False)

        self.map[key] = new_node

    def put(self, key: Any, value: Any, ttl_seconds: int | None = None):
        """Insert or update key with value. Thread-safe wrapper."""
        if self.lock:
            with self.lock:
                return self._put(key, value, ttl_seconds)
        else:
            return self._put(key, value, ttl_seconds)

    def _delete(self, key: Any) -> bool:
        if key in self.map:
            self.map.pop(key)
            return True
        return False

    def delete(self, key: Any) -> bool:
        """Delete key if present. Returns True if removed."""
        if self.lock:
            with self.lock:
                return self._delete(key)
        return self._delete(key)

    def _clear(self):
        """Clear cache."""
        self.map.clear()

    def clear(self):
        if self.lock:
            with self.lock:
                self._clear()
        self._clear()

    def decorator(self, ttl_seconds: int | None = None):
        """
        Returns a function decorator that caches the results of the decorated function.

        Args:
            ttl_seconds (int | None): Overrides the instance's default TTL for the
                                      results of the decorated function.
        """

        def _decor(fn: Callable):
            def wrapper(*args, **kwargs):
                # 1. Build a deterministic cache key from the function and its arguments.
                key = (fn.__module__, fn.__qualname__, args, frozenset(kwargs.items()))

                # 2. Attempt to retrieve the cached result.
                val = self.get(key)
                if val is not None:
                    return val

                # 3. Cache miss: Execute the function.
                result = fn(*args, **kwargs)

                # 4. Store the result in the cache. (Note: Async functions are not handled here)
                self.put(key, result, ttl_seconds=ttl_seconds)
                return result

            # Preserve the original function's name and documentation for introspection/debugging.
            wrapper.__name__ = fn.__name__
            wrapper.__doc__ = fn.__doc__
            return wrapper

        return _decor
