"""just A helper so settings module not imported any where."""

from functools import lru_cache
from typing import Annotated

from app.config.cfg_core import AppConfig, DigiposConfig, Settings


@lru_cache
def get_settings() -> Settings:
    """Return the singleton Settings instance."""
    return Settings()  # type: ignore


def get_digipos_config() -> DigiposConfig:
    """Get the Digipos configuration."""
    return get_settings().digipos


def get_app_config() -> AppConfig:
    """Get the application configuration."""
    return get_settings().app


# Annotated Style For Cleaner Import
DigiposConfigDep = Annotated[DigiposConfig, get_digipos_config]
AppConfigDep = Annotated[AppConfig, get_app_config]
