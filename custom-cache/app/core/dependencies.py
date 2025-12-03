from fastapi import Depends
from typing_extensions import Annotated

from app.core.caching.cache_strategies import CacheDep 
from app.db.session import SessionDep
from app.services.hero_service import HeroService


def get_hero_services(session: SessionDep, cache: CacheDep):
    return HeroService(session=session, cache=cache)


HeroServiceDep = Annotated[HeroService, Depends(get_hero_services)]