r"""Password Hashing dan verifikasi dengan Argon2."""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class Hasher:
    _ph = PasswordHasher()

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash the password using Argon2."""
        return Hasher._ph.hash(password)

    @staticmethod
    def verify_password(hashed_password: str, plain_password: str) -> bool:
        """Verify the hashed password against the plain password."""
        try:
            return Hasher._ph.verify(hashed_password, plain_password)
        except VerifyMismatchError:
            return False
