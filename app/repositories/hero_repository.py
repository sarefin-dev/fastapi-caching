from sqlmodel import Session

from app.models.hero import Hero
from app.schemas.hero import HeroCreate, HeroPublic


class HeroRepository:
    """
    Implements the Repository pattern for the Hero model.
    Handles all persistent (database) operations for Hero entities.
    """

    @staticmethod
    def create_hero(session: Session, data: HeroCreate) -> HeroPublic:
        """
        Creates a new Hero record in the database.

        Args:
            session: The active database session (SQLModel/SQLAlchemy Session).
            data: The validated input data for the new hero (HeroCreate schema).

        Returns:
            The newly created Hero object, transformed into the HeroPublic schema
            (including the assigned database ID).
        """
        db_hero = Hero.model_validate(data)
        session.add(db_hero)
        session.commit()
        session.refresh(db_hero)
        return db_hero

    @staticmethod
    def read_hero(session: Session, hero_id: int) -> HeroPublic:
        """
        Reads a single Hero record from the database by its primary key (ID).

        Args:
            session: The active database session (SQLModel/SQLAlchemy Session).
            hero_id: The ID of the hero to retrieve.

        Returns:
            The Hero ORM object (which satisfies the HeroPublic schema)
            or None if a hero with the given ID is not found.
        """
        return session.get(Hero, hero_id)
