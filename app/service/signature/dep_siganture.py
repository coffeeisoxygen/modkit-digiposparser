from typing import Annotated

from app.service.signature.srv_signature import OtomaxSignatureService
from fastapi import Depends


def get_transaction_signature(
    memberid: str,
    product: str,
    dest: str,
    refid: str,
    pin: str,
    password: str,
    service: OtomaxSignatureService = Depends(OtomaxSignatureService),
) -> str:
    """FastAPI dependency-injectable function for generating OtomaX transaction signature.

    Args:
        memberid: Member ID (will be converted to UPPERCASE)
        product: Product code (will be converted to UPPERCASE)
        dest: Destination phone number (original case)
        refid: Reference/Transaction ID (original case)
        pin: Member PIN (original case)
        password: Member password (original case)
        service: OtomaxSignatureService instance (injected)

    Returns:
        str: Base64 encoded signature with URL-safe characters
    """
    return service.generate_transaction_signature(
        memberid, product, dest, refid, pin, password
    )


TrxSignDep = Annotated[str, Depends(OtomaxSignatureService)]
