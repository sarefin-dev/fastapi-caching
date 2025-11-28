from fastapi import Depends
from typing_extensions import Annotated

from app.core.caching.basic_cache import BasicCacheDep 
from app.db.session import SessionDep
from app.services.hero_service import HeroService


def get_hero_services(session: SessionDep, cache: BasicCacheDep):
    return HeroService(session=session, cache=cache)


HeroServiceDep = Annotated[HeroService, Depends(get_hero_services)]