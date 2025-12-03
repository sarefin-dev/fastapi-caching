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
        for i in range(1, 1000):
            test_hero = Hero(name=f"Hero - {i}", age=10 * i, secret_name=f"secret-{i}")
            session.add(test_hero)
            session.commit()

    session.close()