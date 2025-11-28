from fastapi import Depends
from typing_extensions import Annotated

from app.core.caching.cache_protocols import CacheProtocol
from app.core.settings.config import BasicSettings, get_basic_settings
from app.lib.basic_cache import BasicCache

settings: BasicSettings = get_basic_settings()

GLOBAL_BASIC_CACHE: BasicCache = BasicCache(
    capacity=settings.basic_cache_capacity,
    ttl_seconds=settings.basic_cache_ttl_seconds,
    thread_safe=settings.basic_ccache_thread_safe,
)


def get_cache_service() -> CacheProtocol:
    return GLOBAL_BASIC_CACHE


BasicCacheDep = Annotated[CacheProtocol, Depends(get_cache_service)]
