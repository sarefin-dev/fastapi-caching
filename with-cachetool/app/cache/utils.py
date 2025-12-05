def list_key_generator(x: list[int]) -> str:
    """
    Generates an order-independent, hashable key for the cache.
    1. Sorts the list to ensure [1, 2, 3] and [3, 2, 1] produce the same key.
    2. Joins the elements into a string.
    """
    # Key change: Sort the list 'x' before converting it to strings and joining.
    return "-".join(map(str, sorted(x)))