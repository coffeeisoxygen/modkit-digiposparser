"""configuration for JWT authentication"""

from pydantic import BaseModel


class JwtConfig(BaseModel):
    SECRET_KEY: str
    TOKEN_TYPE: str = "bearer"
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
