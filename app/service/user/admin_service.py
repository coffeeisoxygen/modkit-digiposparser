"""service untuk seeding seeding admin dan lain lain."""

from app.repos.rep_user import UserRepository
from app.service.token.srv_token import TokenService
from app.utils.hasher import Hasher
from loguru import logger

DEFAULT_ADMIN = {
    "username": "admin",
    "name": "Administrator",
    "hashed_password": Hasher.hash_password(
        "Admin123@"
    ),  # <-- reverted to match migration/model
    "is_superuser": True,
    "is_active": True,
}


class AdminService:
    """Service untuk operasi admin: seeding dan login."""

    def __init__(self, repo: UserRepository, token_service: TokenService | None = None):
        self.repo = repo
        self.token_service = token_service

    async def seed_admin(self):
        """Seed admin user jika belum ada."""
        existing_user = await self.repo.get_user_by_username(DEFAULT_ADMIN["username"])
        if existing_user:
            logger.info("Admin user already exists, skipping seeding.")
            return existing_user

        logger.info("Seeding admin user.")
        return await self.repo.create_user(**DEFAULT_ADMIN)

    async def login_admin(self, username: str, password: str):
        """Login admin dan return token jika sukses."""
        if not self.token_service:
            raise ValueError("token_service harus diinisialisasi untuk login.")
        user = await self.repo.get_user_by_username(username)
        if not user:
            logger.warning(f"Login gagal: user '{username}' tidak ditemukan.")
            return None
        if not Hasher.verify_password(password, user.hashed_password):
            logger.warning(f"Login gagal: password salah untuk user '{username}'.")
            return None
        token_data = {
            "sub": user.id,
            "username": user.username,
            "is_superuser": user.is_superuser,
        }
        token = self.token_service.create_access_token(token_data)
        return token
