from typing import Annotated

from app.feature.srv_signature import OtomaxSignatureService
from fastapi import Depends


def get_signature_service() -> OtomaxSignatureService:
    """FastAPI dependency-injectable function for getting OtomaxSignatureService instance."""
    return OtomaxSignatureService()


# Service injection dependency (simplified)
OtomaxSignServiceDep = Annotated[OtomaxSignatureService, Depends(get_signature_service)]
