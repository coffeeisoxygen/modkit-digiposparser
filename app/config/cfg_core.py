from app.config.cfg_app import AppConfig
from app.config.cfg_digipos_credential import DigiposCoreConfig
from app.config.cfg_digipos_response import DigiposRespConfig
from app.config.cfg_jwt import JwtConfig
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with nested configuration.

    >>> Multiple environment files - loading order matters!
    >>> Files loaded in order: .env -> .env.dev/.env.prod (based on APP_ENV)
    >>> Will be overridden by _env_file based on environment
    >>> nested models to make it readable.
    """

    model_config = SettingsConfigDict(
        env_file=(".env"),  # Urutan penting
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_max_split=1,
        env_nested_delimiter="_",
        extra="ignore",
    )

    app: AppConfig
    digipos: DigiposCoreConfig
    jwt: JwtConfig
    digipos_response: DigiposRespConfig
    database_url: str = "sqlite+aiosqlite:///./app.db"
    database_echo: bool = False
