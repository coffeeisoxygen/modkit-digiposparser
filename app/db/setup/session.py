"""database setup.

pake dulu sqlalchemy, dan sqlite , klo nanti mau pake sqlmodel boleh , tapi consider
ada beberapa compleksitas yang harus di fix kan
jadi stick dulu dengan sqlalchemy.
"""

import contextlib
from collections.abc import AsyncIterator

from app.db.setup.base import Base
from app.dependencies.dep_settings import get_settings
from app.exceptions.exc_service import InternalServiceError
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Get database config (url, echo) from dep_settings
settings = get_settings()


class DatabaseSessionManager:
    def __init__(self, host: str):
        self.engine: AsyncEngine | None = create_async_engine(host)
        self._sessionmaker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            autocommit=False, echo=get_settings().database_echo, bind=self.engine
        )

    async def close(self):
        if self.engine is None:
            raise InternalServiceError("Database engine is not initialized")
        await self.engine.dispose()
        self.engine = None
        self._sessionmaker = None  # type: ignore

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self.engine is None:
            raise InternalServiceError("Database engine is not initialized")

        async with self.engine.begin() as connection:
            try:
                yield connection
            except SQLAlchemyError:
                await connection.rollback()
                logger.error("Connection error occurred")
                raise InternalServiceError("Database connection error") from None

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if not self._sessionmaker:
            logger.error("Sessionmaker is not available")
            raise InternalServiceError("Sessionmaker is not available")

        session = self._sessionmaker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Session error could not be established {e}")
            raise InternalServiceError(
                "Session error could not be established"
            ) from None
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(settings.database_url)


async def get_db_session():
    """Get a database session.

    This function provides a database session for the duration of the request.

    Yields:
        AsyncSession: The database session.
    """
    async with sessionmanager.session() as session:
        yield session


# call this with alembic, we use alembic for database migration.
async def create_tables():
    """Create all tables in the database using SQLAlchemy Base metadata.

    This function initializes the database schema by creating tables
    defined in the SQLAlchemy models.
    """
    if sessionmanager.engine is None:
        raise InternalServiceError("Database engine is not initialized")
    async with sessionmanager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
