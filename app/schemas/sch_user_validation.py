"""dsini fungsi fungsi helper buat validasi, pake anotated style buat gaya gaya an aja sih."""

# mostly akan menggunakan regex biar keren

import re
from typing import Annotated


def validate_username(username: str) -> bool:
    """Validates that the username contains only alphanumeric characters.

    Returns True if valid, False otherwise.
    """
    return bool(re.fullmatch(r"[A-Za-z0-9]+", username))


UserNameIsAlNum = Annotated[str, validate_username]


def validate_name(name: str) -> bool:
    """Validates that the name contains only alphabetic characters and spaces.

    Returns True if valid, False otherwise.
    """
    return bool(re.fullmatch(r"[A-Za-z\s]+", name))


NameUserIsAlpha = Annotated[str, validate_name]


def validate_password(password: str) -> bool:
    """Validates that the password meets the required criteria.

    Returns True if valid, False otherwise.
    the password must be at least 8 characters long and contain a mix of letters, numbers, and special characters.
    """
    return bool(re.fullmatch(r"[A-Za-z0-9@#$%^&+=]{8,}", password))


PasswordIsStrong = Annotated[str, validate_password]
