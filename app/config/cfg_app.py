"""app base configuration."""

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    """App configuration settings."""

    environment: str = Field(validation_alias="ENVIRONMENT")
    debugmode: bool = Field(validation_alias="DEBUGMODE")
    loglevel: str = Field(validation_alias="LOGLEVEL")
    version: str = Field(validation_alias="VERSION")
    blockrequest: bool = Field(validation_alias="BLOCKREQUEST")

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }
