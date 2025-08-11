"""Setup LifeSpan before the application starts."""

from contextlib import asynccontextmanager

from app.database.table import sessionmanager
from app.feature.user import AdminSeeding
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application."""
    admin_seeding = AdminSeeding(app.state.user_repo)
    await admin_seeding.seed_admin()

    yield  # Application runs here

    if sessionmanager.engine is not None:
        await sessionmanager.close()
