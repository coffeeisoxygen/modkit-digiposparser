# def get_member_repository(request: Request) -> MemberRepository:
#     """Get member repository from app state."""
#     return request.app.state.member_repo


# def get_auth_service(
#     member_repo: MemberRepository = Depends(get_member_repository),
# ) -> MemberAuthService:
#     """Get the member authentication service."""
#     return MemberAuthService(member_manager=member_repo)
