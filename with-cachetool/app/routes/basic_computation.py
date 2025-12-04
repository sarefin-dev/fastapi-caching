import logging

from cachetools import TTLCache, cached
from fastapi import APIRouter, Query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Basic Computation"], prefix="/compute")

cache = TTLCache(maxsize=30, ttl=5)


# FIX: Sort the list before generating the key
def list_key_generator(x: list[int]) -> str:
    """
    Generates an order-independent, hashable key for the cache.
    1. Sorts the list to ensure [1, 2, 3] and [3, 2, 1] produce the same key.
    2. Joins the elements into a string.
    """
    # Key change: Sort the list 'x' before converting it to strings and joining.
    return "-".join(map(str, sorted(x)))


@cached(cache, key=list_key_generator)
def _compute_sum(x: list[int]) -> int:
    key = list_key_generator(x)
    logger.info(f"Should be called one time for key: {key}")
    return sum(x)


@router.get("/sum")
async def get_sum(q: list[int] = Query()):
    return _compute_sum(q)