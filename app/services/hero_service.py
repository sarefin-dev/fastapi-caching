from sqlmodel import Session

from app.repositories.hero_repository import HeroRepository
from app.schemas.hero import HeroPublic


class HeroService:
    """
    Implements the Service Layer for Hero-related business logic and coordination.

    The Service Layer acts as an intermediary, defining transactional boundaries
    and encapsulating domain-specific rules (currently minimal, focused on data retrieval).
    """

    @staticmethod
    def read_hero(session: Session, hero_id: int) -> HeroPublic:
        """
        Retrieves a Hero by ID by delegating the database access to the repository.

        In a real application, this method would contain additional business logic
        (e.g., validation, permission checks, data transformation) before or after
        calling the repository.

        Args:
            session: The active database session.
            hero_id: The ID of the hero to retrieve.

        Returns:
            The Hero data retrieved by the repository.
        """
        return HeroRepository.read_hero(session=session, hero_id=hero_id)
