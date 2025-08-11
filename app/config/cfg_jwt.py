"""configuration for JWT authentication"""

from pydantic import BaseModel, Field


class JwtConfig(BaseModel):
    SECRET_KEY: str = Field(
        default="ini-bikin-diopen-ssl -rand hex 32-09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
        alias="JWT_SECRET_KEY",
    )
    ALGORITHM: str = Field(default="HS256", alias="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, alias="JWT_MINUTES_EXPIRE")
