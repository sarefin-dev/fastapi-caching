from fastapi import APIRouter, HTTPException, status

from app.db.session import SessionDep
from app.services.hero_service import HeroService
from app.schemas.hero import HeroPublic

router = APIRouter(tags=["Hero"], prefix="/heros")


@router.get("/{hero_id}", response_model=HeroPublic)
def get_hero(hero_id, session: SessionDep):
    """
    Retrieve a single Hero by its ID.

    Args:
        hero_id (int): The unique identifier of the hero.
        session (SessionDep): The active database session injected by FastAPI.

    Raises:
        HTTPException 404: If no hero is found with the given ID.

    Returns:
        HeroPublic: The found hero data conforming to the public schema.
    """
    hero = HeroService.read_hero(session, hero_id)
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot find hero with id {hero_id}",
        )
    return hero
