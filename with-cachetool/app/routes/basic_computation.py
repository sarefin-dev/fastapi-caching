from fastapi import APIRouter, Query

router = APIRouter(
    tags=["Basic Computation"],
    prefix="/compute"
)

@router.get("/sum")
async def get_sum(q: list[int] = Query()):
    return sum(q)