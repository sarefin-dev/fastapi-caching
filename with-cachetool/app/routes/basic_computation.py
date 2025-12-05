import logging

from threading import RLock

from cachetools import TTLCache, cached
from fastapi import APIRouter, Query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Basic Computation"], prefix="/compute")

# CHANGE: Increased TTL to 60 seconds (from 5 or 30 previously)
# Cache size set to 30 max items, with a Time-To-Live (TTL) of 60 seconds.
cache = TTLCache(maxsize=30, ttl=60)

lock = RLock()

# FIX: Sort the list before generating the key
def list_key_generator(x: list[int]) -> str:
    """
    Generates an order-independent, hashable key for the cache.
    1. Sorts the list to ensure [1, 2, 3] and [3, 2, 1] produce the same key.
    2. Joins the elements into a string.
    """
    # Key change: Sort the list 'x' before converting it to strings and joining.
    return "-".join(map(str, sorted(x)))


@cached(cache, lock=lock, key=list_key_generator)
def _compute_sum(x: list[int]) -> int:
    """Computes the sum of a list of integers. Caching is order-independent."""
    key = list_key_generator(x)
    logger.info(f"Should be called one time for key: {key}")
    return sum(x)


# NEW FEATURE: Recursive fibonacci computation with default caching
@cached(cache, lock=lock)
def _compute_fibonacci(n) -> int:
    """
    Docstring for _compute_fibonacci

    :param n: the number for which the fabonacci series will be calculated
    :return: fibonacci series is a series where a number is the sum of two consecutive previous number.
    :rtype: int
    """
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        # This print statement helps verify cache hits/misses
        print(
            f"Computing fibonacci for {n} - it should not be called within 1 min if number <= {n} is given"
        )
        return _compute_fibonacci(n - 2) + _compute_factorial(n - 1)


# NEW FEATURE: Recursive factorial computation with default caching
# The default key generator for @cached uses the function arguments (n) directly.
@cached(cache, lock=lock)
def _compute_factorial(n: int) -> int:
    """
    Computes the factorial of n (n!).
    The TTLCache ensures the result is saved for 'n' for 60 seconds.
    """
    # This print statement helps verify cache hits/misses
    print(
        f"Computing factorial for {n} - it should not be called within 1 min if number <= {n} is given"
    )

    # Base case for recursion
    if n <= 1:
        return 1

    # Recursive step: n * (n-1)!
    return n * _compute_factorial(n - 1)


@router.get("/sum")
async def get_sum(q: list[int] = Query()):
    """Endpoint for computing the sum of integers from a query list (q=1&q=2...)."""
    return _compute_sum(q)


@router.get("/factorial/{n}")
async def get_factorial(n: int) -> int:
    """Endpoint for computing the factorial of an integer 'n'."""
    return _compute_factorial(n)


@router.get("/fibonacci/{n}")
async def get_fibonacci(n: int) -> int:
    """Endpoint for computing the factorial of an integer 'n'."""
    return _compute_fibonacci(n)
