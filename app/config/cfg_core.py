from app.config.cfg_app import AppConfig
from app.config.cfg_digipos import DigiposCoreConfig, DigiposRespConfig
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
    digipos_response: DigiposRespConfig


def main():
    from app.config.dep_settings import get_settings

    settings = get_settings()
    print(settings.app)
    # Dump all settings as dict
    print(settings.model_dump())


if __name__ == "__main__":
    main()
