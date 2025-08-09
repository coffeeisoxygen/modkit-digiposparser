from typing import Annotated

from app.member.rep_member import MemberRepository
from fastapi import Depends


def get_member_repository() -> MemberRepository:
    """Get the member repository.

    This function provides a singleton instance of the MemberRepository
    for dependency injection.

    Returns:
        MemberRepository: The member repository instance.
    """
    return MemberRepository("members.yaml")


MemberRepoDep = Annotated[MemberRepository, Depends(get_member_repository)]
