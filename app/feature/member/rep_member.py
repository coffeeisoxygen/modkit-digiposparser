"""Member Repository.

Repository pattern for member data management:
- Constructor injection with optional file path
- Private methods for internal operations
- Public interface for data access
- Error handling with fallback behavior
- Integration with FileWatcher via reload callback
"""

from pathlib import Path
from typing import Any

import yaml
from app.feature.member.sch_member import MemberInDB
from app.feature.member.srv_memberdata import check_duplicate_memberids
from loguru import logger
from pydantic import ValidationError


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
        """Load data from YAML file and validate it.

        Returns:
            List of validated MemberInDB objects or empty list if file is empty.

        Raises:
            FileNotFoundError: If YAML file doesn't exist
            ValueError: If YAML structure is invalid or duplicates found
            ValidationError: If Pydantic validation fails
        """
        with logger.contextualize(path=self.file_path, operation="load_from_file"):
            # Check file existence
            if not self.file_path.exists():
                logger.error("YAML file not found")
                raise FileNotFoundError(f"YAML file not found: {self.file_path}")

            # Load YAML
            try:
                with self.file_path.open("r", encoding="utf-8") as f:
                    data: Any = yaml.safe_load(f)
            except yaml.YAMLError as e:
                logger.error("Failed to parse YAML file", error=str(e))
                raise ValueError(f"Failed to parse YAML file: {e}") from e

            # Handle empty file
            if not data or "members" not in data:
                logger.warning("File empty or missing 'members' key")
                return []

            members_list = data["members"]
            if not isinstance(members_list, list):
                raise TypeError("'members' must be a list")

            # Check for duplicates BEFORE Pydantic validation
            duplicates = check_duplicate_memberids(members_list)
            if duplicates:
                logger.error("Duplicate memberids found", duplicates=duplicates)
                raise ValueError(f"Duplicate memberids found: {duplicates}")

            # Validate each member with Pydantic
            validated_members: list[MemberInDB] = []
            for i, item in enumerate(members_list):
                try:
                    validated_members.append(MemberInDB(**item))
                except ValidationError as e:
                    logger.error(
                        "Member validation failed", index=i, item=item, error=str(e)
                    )
                    raise ValueError(
                        f"Member validation failed at index {i}: {e}"
                    ) from e

            logger.info(
                "Successfully loaded members from file",
                count=len(validated_members),
                member_ids=[m.memberid for m in validated_members[:5]],  # Log first 5
            )
            return validated_members

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
