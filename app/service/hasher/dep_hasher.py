from typing import Annotated

from app.service.hasher.srv_hasher import HasherService
from fastapi import Depends


def get_hasher_service() -> HasherService:
    """FastAPI dependency-injectable function for getting HasherService instance."""
    return HasherService()


HasherDep = Annotated[HasherService, Depends(get_hasher_service)]
