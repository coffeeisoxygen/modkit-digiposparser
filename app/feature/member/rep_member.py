"""Member Repository.

Repository pattern for member data management:
- Constructor injection with optional file path
- Delegates loading tasks to pure functions in srv_memberdata
- Public interface for data access
- Error handling with fallback behavior
- Integration with FileWatcher via reload callback
"""

from pathlib import Path

from app.feature.member.sch_member import MemberInDB
from app.feature.member.srv_memberdata import load_and_validate_yaml
from loguru import logger


class MemberRepository:
    """Repository for member data with fallback behavior and clean interface."""

    def __init__(self, file_path: Path | str | None = None):
        """Initialize MemberRepository with optional file path.

        Args:
            file_path: Path to members.yaml file. If None, uses default data/members.yaml
        """
        if file_path is None:
            file_path = Path("data/members.yaml")

        self.file_path = Path(file_path)
        self._members: list[MemberInDB] = []
        self._members_dict: dict[str, MemberInDB] = {}

        logger.info("Initializing MemberRepository", path=self.file_path)
        self.reload()

    def _load_data_from_file(self) -> list[MemberInDB]:
        """Load data by delegating to pure function in srv_memberdata.

        Returns:
            List of validated MemberInDB objects or empty list if file is empty.

        Raises:
            FileNotFoundError: If YAML file doesn't exist
            ValueError: If YAML structure is invalid or duplicates found
            ValidationError: If Pydantic validation fails
        """
        # Delegate all loading logic to pure function
        return load_and_validate_yaml(self.file_path)

    def reload(self) -> None:
        """Reload all data from file and update internal state.

        Uses fallback behavior - if reload fails, keeps existing data and logs error.
        This ensures the repository remains functional even if file becomes temporarily invalid.
        """
        logger.info("Starting MemberRepository reload")
        try:
            new_members = self._load_data_from_file()

            # Update both list and dict storage
            self._members = new_members
            self._members_dict = {m.memberid: m for m in new_members}

            logger.info(
                "MemberRepository reload completed successfully", count=len(new_members)
            )

        except FileNotFoundError as e:
            # Only fallback if we already have data loaded, else propagate
            if not self._members:
                logger.error(
                    "Member data file not found during initial load",
                    error=str(e),
                    path=str(self.file_path),
                )
                raise
            logger.error(
                "Failed to reload member data, keeping existing data",
                error=str(e),
                current_count=len(self._members),
            )
        except Exception as e:
            # Fallback behavior - keep existing data on reload failure
            logger.error(
                "Failed to reload member data, keeping existing data",
                error=str(e),
                current_count=len(self._members),
            )
            # Don't re-raise - this allows the repository to continue functioning

    def get_member_by_id(self, memberid: str) -> MemberInDB | None:
        """Get member by ID with O(1) lookup."""
        member = self._members_dict.get(memberid)
        if member:
            logger.debug("Member found", memberid=memberid)
        else:
            logger.debug("Member not found", memberid=memberid)
        return member

    def get_all_members(self) -> list[MemberInDB]:
        """Get all members as a copy of the internal list."""
        return self._members.copy()

    def get_member_count(self) -> int:
        """Get total number of members."""
        return len(self._members)

    def is_member_active(self, memberid: str) -> bool:
        """Quick check if member exists and is active."""
        member = self.get_member_by_id(memberid)
        return member is not None and member.is_active

    def check_allow_nosign(self, memberid: str) -> bool:
        """Check if member allows authentication without signature."""
        member = self.get_member_by_id(memberid)
        return member is not None and member.allow_nosign

    def get_member_ids(self) -> list[str]:
        """Get all member IDs."""
        return list(self._members_dict.keys())

    def has_member(self, memberid: str) -> bool:
        """Check if member exists."""
        return memberid in self._members_dict

    def clear_data(self) -> None:
        """Clear all stored data (useful for testing)."""
        self._members.clear()
        self._members_dict.clear()
        logger.info("Member data cleared from repository")
