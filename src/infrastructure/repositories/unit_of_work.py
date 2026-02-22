from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from infrastructure.repositories.task_repository import TaskRepository

class UnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        """Initialize Unit of Work with session factory."""
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> UnitOfWork:
        """Start a new database session and initialize repositories."""
        # Create new session
        self._session = self._session_factory()
        # Add repositories
        self.tasks = TaskRepository(self._session)
        
        return self
    
    async def __aexit__(
            self,
            exception_type: type[BaseException] | None,
            exception_value: BaseException | None, 
            exception_traceback: Any
        ) -> None:
        """Exit context manager, committing or rollbacking session."""
        if exception_type is not None:
            # Exception occurred, rollback
            await self._session.rollback()
        
        # Always close session
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def commit(self) -> None:
        """Commit the current transaction."""
        if self._session is None:
            raise RuntimeError("Cannot commit: no active session")

        await self._session.commit()

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        if self._session is None:
            raise RuntimeError("Cannot rollback: no active session")

        await self._session.rollback()
