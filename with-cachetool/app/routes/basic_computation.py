from app.services.computer_service import (
    _compute_factorial,
    _compute_fibonacci,
    _compute_sum,
)
from fastapi import APIRouter, Query

router = APIRouter(tags=["Basic Computation"], prefix="/compute")


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
