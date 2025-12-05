from cachetools import LRUCache, TTLCache
from threading import RLock

lruCache = LRUCache(maxsize=30)

ttlCache = TTLCache(maxsize=30, ttl=60)

lock = RLock()

def get_lock():
    return lock

def get_cache_client():
    return lruCache

