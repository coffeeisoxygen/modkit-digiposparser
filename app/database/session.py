import contextlib
from collections.abc import AsyncIterator

from app.dependencies.dep_settings import get_settings
from app.exceptions.exceptions import ServiceError
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

settings = get_settings()


class DatabaseSessionManager:
    def __init__(self, host: str):
        self.engine: AsyncEngine | None = create_async_engine(host)
        self._sessionmaker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
            echo=settings.database_echo,
        )

    async def close(self):
        if self.engine is None:
            raise ServiceError("Engine is already disposed")
        await self.engine.dispose()
        self.engine = None
        self._sessionmaker = None  # type: ignore

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self.engine is None:
            raise ServiceError("Engine not initialized")
        async with self.engine.connect() as connection:
            try:
                yield connection
            except SQLAlchemyError as e:
                logger.error(f"Connection error occurred: {e}")
                raise ServiceError from e

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if not self._sessionmaker:
            logger.error("Sessionmaker is not available")
            raise ServiceError("Sessionmaker is not available")

        async with self._sessionmaker() as session:
            try:
                yield session
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Session error occurred: {e}")
                raise ServiceError("Could not establish session") from e


sessionmanager = DatabaseSessionManager(settings.database_url)


async def get_db_session():
    """FastAPI dependency to get DB session."""
    async with sessionmanager.session() as session:
        yield session
