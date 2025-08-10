from typing import Annotated

from app.feature.srv_hasher import HasherService
from fastapi import Depends


def get_hasher_service() -> HasherService:
    """FastAPI dependency-injectable function for getting HasherService instance."""
    return HasherService()


HasherServiceDep = Annotated[HasherService, Depends(get_hasher_service)]
