import time
import threading
from typing_extensions import Any, Callable

from app.core.caching.cache_protocols import CacheProtocol


class _Node:
    """Represents a node in the doubly linked list, storing cache data and pointers."""

    __slots__ = ("key", "value", "prev", "next", "expiry")

    def __init__(self, key=None, value=None, expiry: float | None = None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None
        # Unix timestamp when the item should expire (seconds since epoch)
        self.expiry = expiry


class BasicCache(CacheProtocol):
    """
    A Thread-Safe, Time-To-Live (TTL) enabled Least Recently Used (LRU) Cache.
    Uses a combination of a hash map (for O(1) lookup) and a doubly linked list
    (for O(1) recency updates and eviction).
    """

    def __init__(
        self,
        capacity: int,
        ttl_seconds: int | None = None,
        thread_safe: bool = False,
    ):
        """
        Initializes the LRU Cache structure.

        Args:
            capacity: The maximum number of items the cache can hold (must be > 0).
            ttl_seconds: The time-to-live in seconds for cached items. None means no expiration.
            thread_safe: If True, adds a threading lock for safe access from multiple threads.
        """
        if capacity <= 0:
            raise ValueError("capacity must be > 0")

        self.capacity = int(capacity)
        self.ttl = ttl_seconds
        self.map = {}  # key -> _Node (The hash map for O(1) lookup)

        # --- Doubly Linked List Setup ---
        # Dummy head node (DH): The node immediately following DH is the Most Recently Used (MRU).
        self.head = _Node()
        # Dummy tail node (DT): The node immediately preceding DT is the Least Recently Used (LRU).
        self.tail = _Node()

        # Link the dummy head and tail to create an empty list structure.
        self.head.next = self.tail
        self.tail.prev = self.head

        # Initialize a threading lock if thread_safe is requested.
        self.lock = threading.Lock() if thread_safe else None

    def _add_node_to_front(self, node: _Node):
        """
        Adds a new node immediately after the dummy head (MRU position).

        Example:
        Current state: DH <-> A <-> DT
        Steps: X.prev=DH, X.next=A, A.prev=X, DH.next=X
        Final state: DH <-> X <-> A <-> DT
        """
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def _remove_node(self, node: _Node):
        """
        Removes a node from its current position in the doubly linked list.

        This operation is performed in O(1) time by updating the pointers
        of the preceding and succeeding nodes to bypass the target node.

        Example:
        Current state: ... <-> A <-> node <-> B <-> ...
        Final state: ... <-> A <-> B <-> ...
        """
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = node.next = None

    def _move_to_front(self, node: _Node):
        """
        Moves an existing node to the front of the list, making it the Most Recently Used (MRU) item.

        This is performed on a cache hit to update recency.

        Example:
        Current state: DH <-> A <-> node <-> B <-> DT
        Final state: DH <-> node <-> A <-> B <-> DT
        """
        # 1. Detach the node from its current position.
        self._remove_node(node)

        # 2. Re-insert the detached node immediately after the dummy head.
        self._add_node_to_front(node)

    def _pop_lru(self) -> _Node:
        """
        Identifies and removes the Least Recently Used (LRU) node (the one before the tail).

        Called when the cache reaches its capacity (eviction).

        Returns:
            The removed LRU node object, or None if the list is empty.
        """
        lru = self.tail.prev

        # Check if the list is empty (DH is pointing directly to DT)
        if lru is self.head:
            return None

        self._remove_node(lru)
        return lru

    def _get(self, key: Any) -> Any | None:
        """
        Retrieves a value, handling TTL check and recency update. (Internal, non-locking)
        """
        node = self.map.get(key)
        if not node:
            return None

        # Check Expiry: If expired, clean up and return None (cache miss).
        if self._is_expired(node):
            self._remove_node(node)
            del self.map[key]
            return None

        # Update Recency (Cache Hit): Move the node to the front.
        self._move_to_front(node)
        return node.value

    def _put(self, key: Any, value: Any, ttl_seconds: int | None = None):
        """
        Inserts or updates an item in the cache, handling TTL and eviction. (Internal, non-locking)
        """
        node = self.map.get(key)
        expiry = None

        # Calculate effective TTL and expiry time.
        effective_ttl = self.ttl if ttl_seconds is None else ttl_seconds
        if effective_ttl is not None:
            expiry = self._now() + effective_ttl

        if node:
            # Cache Hit (Update): Update value/expiry and move to MRU.
            node.value = value
            node.expiry = expiry
            self._move_to_front(node)
            return

        # Cache Miss (Insert):
        new_node = _Node(key=key, value=value, expiry=expiry)
        self.map[key] = new_node
        self._add_node_to_front(new_node)

        # Check Eviction: If over capacity, remove the LRU node from the list and map.
        if len(self.map) > self.capacity:
            lru = self._pop_lru()
            if lru:
                self.map.pop(lru.key, None)

    def _delete(self, key: Any) -> bool:
        """Removes an item from the map and linked list. (Internal, non-locking)"""
        node = self.map.pop(key, None)
        if not node:
            return False
        self._remove_node(node)
        return True

    def _clear(self):
        """Resets the cache map and linked list to an empty state. (Internal, non-locking)"""
        self.map.clear()
        self.head.next = self.tail
        self.tail.prev = self.head

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

    def get(self, key: Any) -> Any | None:
        """Return value for key, or None if missing/expired. Thread-safe wrapper."""
        if self.lock:
            with self.lock:
                return self._get(key)
        else:
            return self._get(key)

    def put(self, key: Any, value: Any, ttl_seconds: int | None = None):
        """Insert or update key with value. Thread-safe wrapper."""
        if self.lock:
            with self.lock:
                return self._put(key, value, ttl_seconds)
        else:
            return self._put(key, value, ttl_seconds)

    def delete(self, key: Any) -> bool:
        """Delete key if present. Returns True if removed. Thread-safe wrapper."""
        if self.lock:
            with self.lock:
                return self._delete(key)
        else:
            return self._delete(key)

    def clear(self):
        """Clear cache. Thread-safe wrapper."""
        if self.lock:
            with self.lock:
                return self._clear()
        else:
            return self._clear()

    def keys(self):
        """Iterates through keys from MRU -> LRU, skipping expired items."""
        cur = self.head.next
        while cur is not self.tail:
            if not self._is_expired(cur):
                yield cur.key
            cur = cur.next

    def values(self):
        """Iterates through values from MRU -> LRU, skipping expired items."""
        cur = self.head.next
        while cur is not self.tail:
            if not self._is_expired(cur):
                yield cur.value
            cur = cur.next

    def items(self):
        """Iterates through (key, value) pairs from MRU -> LRU, skipping expired items."""
        cur = self.head.next
        while cur is not self.tail:
            if not self._is_expired(cur):
                yield (cur.key, cur.value)
            cur = cur.next

    # decorator convenience
    def decorator(self, ttl_seconds: int | None = None):
        """
        Returns a decorator that caches function results using the same LRU instance.

        Args:
            ttl_seconds (int | None): The TTL to use for results from the decorated function.
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
