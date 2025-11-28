from fastapi import Depends
from typing_extensions import Annotated

from app.db.session import SessionDep
from app.services.hero_service import HeroService


def get_hero_services(session: SessionDep):
    return HeroService(session=session)


HeroServiceDep = Annotated[HeroService, Depends(get_hero_services)]
