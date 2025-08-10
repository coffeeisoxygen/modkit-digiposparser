from app.dependencies.dep_siganture import get_signature_service
from app.feature.member import MemberAuthService
from app.feature.member.rep_member import MemberRepository
from app.feature.srv_signature import OtomaxSignatureService
from fastapi import Depends, Request


def get_member_repository(request: Request) -> MemberRepository:
    """Get member repository from app state."""
    return request.app.state.member_repo


def get_auth_service(
    member_repo: MemberRepository = Depends(get_member_repository),
    signature_service: OtomaxSignatureService = Depends(get_signature_service),
) -> MemberAuthService:
    """Get the member authentication service."""
    return MemberAuthService(
        member_manager=member_repo, otomax_sign_service=signature_service
    )
