from fastapi import Depends
from sqlmodel import Session, create_engine
from typing_extensions import Annotated

from app.core.settings.config import get_basic_settings

settings = get_basic_settings()
db_url = settings.database_url

# --- Engine Configuration ---
# Set up arguments specific to the database dialect
# This is required for SQLite when running in a multi-threaded/async environment like FastAPI
connect_args = {"check_same_thread": False}
engine = create_engine(db_url, connect_args=connect_args)


def get_session():
    """
    Dependency generator that yields a new database Session.
    """
    with Session(engine) as session:
        yield session


# Use this dependency whenever a function needs access to the Databse Session object.
SessonDep = Annotated[Session, Depends(get_session)]
