"""Member Manager Service.

Simplified single-responsibility service that handles all member-related operations:
- Loading from YAML
- In-memory storage with O(1) lookup
- Validation with Pydantic
- Reload capability for FileWatcher integration
"""

from pathlib import Path
from typing import Any

import yaml
from app.feature.member.sch_member import MemberInDB
from loguru import logger
from pydantic import ValidationError


class MemberManager:
    """Manages member data lifecycle - loading, validation, and access."""

    def __init__(self, yaml_path: str | Path):
        self.yaml_path = Path(yaml_path)
        self._members_dict: dict[str, MemberInDB] = {}
        self._members_list: list[MemberInDB] = []

    def initialize(self) -> None:
        """Load members from YAML and set up in-memory storage."""
        with logger.contextualize(path=self.yaml_path, operation="initialize"):
            logger.info("Initializing member data")

            # Load and validate members
            members = self._load_and_validate_yaml()

            # Store in both dict (for O(1) lookup) and list (for iteration)
            self._members_dict = {m.memberid: m for m in members}
            self._members_list = members

            logger.info(
                "Successfully initialized member data",
                count=len(members),
                member_ids=[m.memberid for m in members[:5]],  # Log first 5 IDs
            )

    def reload(self) -> None:
        """Reload members from YAML - called by FileWatcher."""
        with logger.contextualize(operation="reload"):
            logger.info("Reloading member data due to file change")
            try:
                self.initialize()
                logger.info("Member data reload completed successfully")
            except Exception as e:
                logger.error("Failed to reload member data", error=str(e))
                # Keep existing data on reload failure
                raise

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

    def _load_and_validate_yaml(self) -> list[MemberInDB]:
        """Load YAML file and validate each member with Pydantic."""
        # Check file existence
        if not self.yaml_path.exists():
            logger.error("YAML file not found")
            raise FileNotFoundError(f"YAML file not found: {self.yaml_path}")

        # Load YAML
        try:
            with self.yaml_path.open("r", encoding="utf-8") as f:
                data: Any = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error("Failed to parse YAML file", error=str(e))
            raise ValueError(f"Failed to parse YAML file: {e}") from e

        # Validate structure
        if not isinstance(data, dict) or "members" not in data:
            raise ValueError("YAML must contain 'members' key")

        members_list = data["members"]
        if not isinstance(members_list, list):
            raise TypeError("'members' must be a list")

        # Validate each member with Pydantic
        validated_members: list[MemberInDB] = []
        for i, item in enumerate(members_list):
            try:
                validated_members.append(MemberInDB(**item))
            except ValidationError as e:
                logger.error(
                    "Member validation failed", index=i, item=item, error=str(e)
                )
                raise ValueError(f"Member validation failed at index {i}: {e}") from e

        if not validated_members:
            logger.warning("No valid members found in YAML file")

        return validated_members
