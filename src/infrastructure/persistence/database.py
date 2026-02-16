from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass

def create_database_engine() -> AsyncEngine:
    return create_async_engine("sqlite+aiosqlite:///db.sqlite", echo=True, future=True)

def create_session_factory(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(
        engine,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
