from app.repos.rep_user import User, UserRepository
from loguru import logger




class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_user(self, user_id: int):
        logger.info(f"Fetching user with ID: {user_id}")
        return await self.repo.get_user_by_id(user_id)

    async def create_user(self, user_data: dict) -> User:
        user = User(**user_data)
        logger.info(f"Creating user: {user.username}")
        return await self.repo.create_user(user)
