# ruff :noqa  D103,RUF029
from app.database.session import get_db_session
from app.repos.rep_user import UserRepository
from app.service.token.srv_token import TokenService
from app.service.user.admin_service import AdminService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_repository(
    db: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    return UserRepository(db)


async def get_token_service() -> TokenService:
    return TokenService()


async def get_admin_service(
    repo: UserRepository = Depends(get_user_repository),
    token_service: TokenService = Depends(get_token_service),
) -> AdminService:
    return AdminService(repo=repo, token_service=token_service)
