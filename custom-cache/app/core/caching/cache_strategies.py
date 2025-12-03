from fastapi import Depends
from typing_extensions import Annotated

from app.cachelib.basic_cache import BasicCache
from app.cachelib.order_dict_cache import OrderDictCache
from app.core.caching.cache_protocols import CacheProtocol
from app.core.settings.config import BasicSettings, get_basic_settings

settings: BasicSettings = get_basic_settings()

GLOBAL_BASIC_CACHE: BasicCache = BasicCache(
    capacity=settings.cache_capacity,
    ttl_seconds=settings.cache_ttl_seconds,
    thread_safe=settings.cache_thread_safe,
)

GLOBAL_ORDERDICT_CACHE: OrderDictCache = OrderDictCache(
    capacity=settings.cache_capacity,
    ttl_seconds=settings.cache_ttl_seconds,
    thread_safe=settings.cache_thread_safe,
)


def get_cache_strategies() -> CacheProtocol:
    if settings.cache_engine == "ORDER_DICT":
        return GLOBAL_ORDERDICT_CACHE
    return GLOBAL_BASIC_CACHE


CacheDep = Annotated[CacheProtocol, Depends(get_cache_strategies)]
