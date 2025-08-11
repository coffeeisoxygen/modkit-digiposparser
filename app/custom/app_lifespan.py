from contextlib import asynccontextmanager

from app.database.session import sessionmanager
from app.repos.rep_user import UserRepository
from app.service.token.srv_token import TokenService
from app.service.user.admin_service import AdminService
from fastapi import FastAPI
from loguru import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application."""
    logger.info("Starting application...")

    # Seed admin sebelum aplikasi jalan
    async with sessionmanager.session() as session:
        repo = UserRepository(session)
        token_service = TokenService()  # Instantiate token service
        seeder = AdminService(repo, token_service)  # Pass token_service as argument
        await seeder.seed_admin()

    yield  # aplikasi jalan disini

    if sessionmanager.engine is not None:
        await sessionmanager.close()
