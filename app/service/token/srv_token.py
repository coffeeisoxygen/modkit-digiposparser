from datetime import datetime, timedelta

import jwt
from app.dependencies import get_settings
from app.exceptions.exceptions import InvalidTokenError, ServiceError

settings = get_settings()

SECRET_KEY = settings.jwt.SECRET_KEY
ALGORITHM = settings.jwt.ALGORITHM
ACCESS_TOKEN_TYPE = settings.jwt.TOKEN_TYPE
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt.ACCESS_TOKEN_EXPIRE_MINUTES


class TokenService:
    """Token service for creating and decoding JWT tokens.

    This service provides methods to create and decode JWT tokens for user authentication.

    Raises:
        ServiceError: If there is an error while creating or decoding the token.
        InvalidTokenError: If the token is invalid or expired.

    Returns:
        str: The encoded JWT token.
        dict: The decoded payload of the JWT token.
    """

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise ServiceError("Token expired") from None
        except jwt.PyJWTError:
            raise InvalidTokenError("Invalid token") from None
        else:
            return payload
