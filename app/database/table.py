from app.database.session import sessionmanager
from app.models import Base


# Create tables helper
async def create_tables():
    """Create all database tables.

    This function creates all tables defined in the SQLAlchemy models.
    """
    async with sessionmanager.engine.begin() as conn:  # type: ignore
        await conn.run_sync(
            lambda sync_conn: Base.metadata.create_all(sync_conn, checkfirst=True)
        )
