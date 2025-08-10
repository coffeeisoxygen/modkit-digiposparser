from app.dependencies.dep_siganture import OtomaxSignatureService, get_signature_service
from app.feature.member import MemberAuthService, MemberManager
from fastapi import Depends


def get_member_manager():
    """Data ada di appstate."""
    return app.state.member_manager  # type: ignore  # noqa: F821


def get_auth_service(
    member_manager: MemberManager = Depends(get_member_manager),
    signature_service: OtomaxSignatureService = Depends(
        dependency=get_signature_service
    ),
) -> MemberAuthService:
    """Get the member authentication service."""
    return MemberAuthService(
        member_manager=member_manager, otomax_sign_service=signature_service
    )
