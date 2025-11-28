from app.db.session import SessionDep
from app.repositories.hero_repository import HeroRepository
from app.schemas.hero import HeroPublic


class HeroService:
    """
    Implements the Service Layer for Hero-related business logic and coordination.

    The Service Layer acts as an intermediary, defining transactional boundaries
    and encapsulating domain-specific rules (currently minimal, focused on data retrieval).
    """

    def __init__(self, session: SessionDep):
        self.session = session


    def read_hero(self, hero_id: int) -> HeroPublic:
        """
        Retrieves a Hero by ID by delegating the database access to the repository.

        Args:
            hero_id: The ID of the hero to retrieve.

        Returns:
            The Hero data retrieved by the repository.
        """
        return HeroRepository.read_hero(session=self.session, hero_id=hero_id)
