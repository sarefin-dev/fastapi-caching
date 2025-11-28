from sqlmodel import SQLModel, select

from app.db.session import engine, get_session
from app.models.hero import Hero

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_db_and_tables():
    """
    Creates all database tables and seeds initial data IF the database is empty.
    """
    SQLModel.metadata.create_all(engine)

    session = next(get_session())
    existing_hero = session.exec(select(Hero)).first() #for checking if database has data.

    if existing_hero:
        logger.info("Data already exists in database")
    else:
        logger.info("Seeding database with initial data")
        test_hero = Hero(name="First Hero", age=10, secret_name="secret")
        session.add(test_hero)
        session.commit()

    session.close()