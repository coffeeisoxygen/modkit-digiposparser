from app.exceptions.exceptions import AuthenticationFailedError
from app.models.user import User
from app.repos.rep_user import UserRepository
from app.service.token.srv_token import TokenService
from app.utils.hasher import Hasher
from loguru import logger

DEFAULT_ADMIN = {
    "username": "admin",
    "name": "Administrator",
    "hashed_password": Hasher.hash_password("Admin123@"),
    "is_superuser": True,
    "is_active": True,
}


class AdminService:
    """Service untuk operasi admin: seeding dan login."""

    def __init__(
        self,
        repo: UserRepository,
        token_service: TokenService | None = None,
    ):
        self.repo = repo
        self.token_service: TokenService | None = token_service

    async def seed_admin(self) -> User:
        """Seed admin user jika belum ada."""
        existing_user = await self.repo.get_user_by_username(DEFAULT_ADMIN["username"])
        if existing_user:
            logger.info("Admin user sudah ada, skip seeding.")
            return existing_user

        logger.info("Seeding admin user baru.")
        return await self.repo.create_user(**DEFAULT_ADMIN)

    async def login_admin(self, username: str, password: str) -> str | None:
        """Login admin, kembalikan JWT token jika sukses, None jika gagal."""
        if not self.token_service:
            raise ValueError("Token service harus diinisialisasi untuk login.")

        def raise_user_not_found():
            logger.warning(f"Login gagal: user '{username}' tidak ditemukan.")
            raise AuthenticationFailedError("User tidak ditemukan.")

        def raise_wrong_password():
            logger.warning(f"Login gagal: password salah untuk user '{username}'.")
            raise AuthenticationFailedError("Password salah.")

        try:
            user = await self.repo.get_user_by_username(username)
            if not user:
                raise_user_not_found()
            elif not Hasher.verify_password(password, user.hashed_password):
                raise_wrong_password()
            else:
                token_data = {
                    "sub": user.id,
                    "username": user.username,
                    "is_superuser": user.is_superuser,
                }
                token = self.token_service.create_access_token(token_data)
                return token
        except AuthenticationFailedError as e:
            logger.error(f"Login admin gagal: {e}")
            return None
