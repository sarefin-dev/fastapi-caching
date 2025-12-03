from app.core.caching.cache_protocols import CacheProtocol
from app.db.session import SessionDep
from app.repositories.hero_repository import HeroRepository
from app.schemas.hero import HeroPublic


class HeroService:
    """
    Implements the Service Layer for Hero-related business logic and coordination.

    The Service Layer acts as an intermediary, defining transactional boundaries
    and encapsulating domain-specific rules (currently minimal, focused on data retrieval).
    """

    def __init__(self, session: SessionDep, cache: CacheProtocol):
        self.session = session
        self.cache = cache

    @staticmethod
    def _hero_cache_key(hero_id: int) -> str:
        return f"hero:{hero_id}"

    def read_hero(self, hero_id: int) -> HeroPublic:
        """
        Retrieves a Hero by ID by delegating the database access to the repository.

        Args:
            hero_id: The ID of the hero to retrieve.

        Returns:
            The Hero data retrieved by the repository.
        """
        cache_key = HeroService._hero_cache_key(hero_id=hero_id)
        cached_hero_data = self.cache.get(cache_key)

        if cached_hero_data:
            print("serving from cache...")
            return cached_hero_data

        db_hero_data = HeroRepository.read_hero(session=self.session, hero_id=hero_id)

        if db_hero_data:
            self.cache.put(cache_key, db_hero_data)

        return db_hero_data
