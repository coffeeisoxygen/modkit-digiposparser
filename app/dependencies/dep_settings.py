"""just A helper so settings module not imported any where."""

from functools import lru_cache
from typing import Annotated

from app.config.cfg_core import (
    AppConfig,
    DigiposCoreConfig,
    DigiposRespConfig,
    Settings,
)


@lru_cache
def get_settings() -> Settings:
    """Return the singleton Settings instance."""
    return Settings()  # type: ignore


def get_digipos_config() -> DigiposCoreConfig:
    """Get the Digipos configuration."""
    return get_settings().digipos


def get_app_config() -> AppConfig:
    """Get the application configuration."""
    return get_settings().app


def get_digipos_response() -> DigiposRespConfig:
    """Get the Digipos response configuration."""
    return get_settings().digipos_response


def get_database_config() -> tuple[str, bool]:
    """Get the database configuration (url, echo)."""
    settings = get_settings()
    return settings.database_url, settings.echo


# Annotated Style For Cleaner Import
DigiposConfigDep = Annotated[DigiposCoreConfig, get_digipos_config]
AppConfigDep = Annotated[AppConfig, get_app_config]
DigiposResponseDep = Annotated[DigiposRespConfig, get_digipos_response]
DatabaseConfigDep = Annotated[tuple[str, bool], get_database_config]
