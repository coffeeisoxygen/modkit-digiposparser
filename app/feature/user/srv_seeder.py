"""service untuk seeding seeding admin dan lain lain."""

from app.feature.utils.hasher import Hasher
from app.repos.rep_user import UserRepository
from loguru import logger

DEFAULT_ADMIN = {
    "username": "admin",
    "name": "Administrator",
    "hashed_password": Hasher.hash_password("Admin123@"),  # <-- changed field name
    "is_superuser": True,
    "is_active": True,
}


class AdminSeeding:
    """Service untuk seeding admin user."""

    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def seed_admin(self):
        """Seed admin user jika belum ada."""
        existing_user = await self.repo.get_user_by_username(DEFAULT_ADMIN["username"])
        if existing_user:
            logger.info("Admin user already exists, skipping seeding.")
            return existing_user

        logger.info("Seeding admin user.")
        # Pass as dict, let repo handle model creation
        return await self.repo.create_user(**DEFAULT_ADMIN)
