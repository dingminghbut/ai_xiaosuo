"""Database models initialization."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, scoped_session

from ai_xiaosuo.config import DATABASE_PATH


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# Create engine
engine = create_engine(
    f"sqlite:///{DATABASE_PATH}",
    echo=False,
    connect_args={"check_same_thread": False}
)

# Create session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


def init_db():
    """Initialize database tables."""
    from ai_xiaosuo.models.project import Project
    from ai_xiaosuo.models.chapter import Chapter
    from ai_xiaosuo.models.character import Character
    from ai_xiaosuo.models.event import Event
    from ai_xiaosuo.models.outline import Outline
    from ai_xiaosuo.models.foreshadowing import Foreshadowing
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    """Get a database session."""
    return Session()


# Import all models to make them available
from ai_xiaosuo.models.project import Project
from ai_xiaosuo.models.chapter import Chapter
from ai_xiaosuo.models.character import Character
from ai_xiaosuo.models.event import Event
from ai_xiaosuo.models.outline import Outline
from ai_xiaosuo.models.foreshadowing import Foreshadowing

__all__ = ["Base", "engine", "Session", "init_db", "get_session", 
           "Project", "Chapter", "Character", "Event", "Outline", "Foreshadowing"]
