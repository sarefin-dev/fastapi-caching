import logging

from cachetools import cached

from app.cache.cache_client import get_cache_client, get_lock
from app.cache.utils import list_key_generator
from app.core.logging_config import APPLICATION_LOGGER_NAME

logger = logging.getLogger(APPLICATION_LOGGER_NAME)

cache = get_cache_client()

lock = get_lock()


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
        logger.info(
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
    logger.info(
        f"Computing factorial for {n} - it should not be called within 1 min if number <= {n} is given"
    )

    # Base case for recursion
    if n <= 1:
        return 1

    # Recursive step: n * (n-1)!
    return n * _compute_factorial(n - 1)
