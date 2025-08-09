from argon2 import PasswordHasher
from argon2 import exceptions as argon2_exceptions


class HasherService:
    """Service for hashing passwords and generating secure keys."""

    def __init__(self):
        self._ph = PasswordHasher()

    def hash_password(self, password: str) -> str:
        """Hash a password using Argon2."""
        return self._ph.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against the given Argon2 hash."""
        try:
            return self._ph.verify(hashed_password, password)
        except argon2_exceptions.VerifyMismatchError:
            return False
        except Exception:
            return False
