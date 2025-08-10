"""Member Manager Service - New Clean Version.

Pure storage and access service for member data:
- In-memory storage with O(1) lookup
- Access methods (get, list, count, etc.)
- No file operations, no validation, no watching
"""

from app.feature.member.sch_member import MemberInDB
from loguru import logger


class MemberManager:
    """Pure storage and access manager for member data."""

    def __init__(self):
        self._members_dict: dict[str, MemberInDB] = {}
        self._members_list: list[MemberInDB] = []

    def update_data(
        self, members_dict: dict[str, MemberInDB], members_list: list[MemberInDB]
    ) -> None:
        """Update internal storage with new data."""
        self._members_dict = members_dict
        self._members_list = members_list
        logger.info("Member data updated in storage", count=len(members_dict))

    def get_member(self, memberid: str) -> MemberInDB | None:
        """Get member by ID with O(1) lookup."""
        return self._members_dict.get(memberid)

    def list_members(self) -> list[MemberInDB]:
        """Get all members as list."""
        return self._members_list.copy()

    def get_member_count(self) -> int:
        """Get total number of members."""
        return len(self._members_dict)

    def is_member_active(self, memberid: str) -> bool:
        """Quick check if member exists and is active."""
        member = self.get_member(memberid)
        return member is not None and member.is_active

    def check_allow_nosign(self, memberid: str) -> bool:
        """Check if member allows authentication without signature."""
        member = self.get_member(memberid)
        return member is not None and member.allow_nosign

    def get_member_ids(self) -> list[str]:
        """Get all member IDs."""
        return list(self._members_dict.keys())

    def has_member(self, memberid: str) -> bool:
        """Check if member exists."""
        return memberid in self._members_dict

    def clear_data(self) -> None:
        """Clear all stored data."""
        self._members_dict.clear()
        self._members_list.clear()
        logger.info("Member data cleared from storage")
