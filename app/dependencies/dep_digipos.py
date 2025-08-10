"""Dependencies untuk Digipos services."""

from typing import Annotated

from app.config.cfg_core import DigiposCoreConfig
from app.dependencies.dep_settings import get_digipos_config
from app.feature.digipos.srv_digipos_url_builder import DigiposUrlBuilder
from fastapi import Depends


def get_digipos_url_builder(
    digipos_config: DigiposCoreConfig = Depends(get_digipos_config),
) -> DigiposUrlBuilder:
    """Get DigiposUrlBuilder service with config dependency."""
    return DigiposUrlBuilder(digipos_config)


# Annotated dependency
DigiposUrlBuilderDep = Annotated[DigiposUrlBuilder, Depends(get_digipos_url_builder)]
