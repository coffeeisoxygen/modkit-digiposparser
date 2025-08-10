"""Member Data Services.

Pure data operations for member management:
- Duplicate checking
- Data reloading
- YAML processing
"""

from pathlib import Path
from typing import Any

import yaml
from app.feature.member.sch_member import MemberInDB
from loguru import logger
from pydantic import ValidationError


def check_duplicate_memberids(members_data: list[dict]) -> list[str]:
    """Check for duplicate memberids, return list of duplicates."""
    seen_ids = set()
    duplicates = []

    for member in members_data:
        memberid = member.get("memberid")
        if memberid in seen_ids:
            duplicates.append(memberid)
        else:
            seen_ids.add(memberid)

    return duplicates


def load_and_validate_yaml(yaml_path: Path) -> list[MemberInDB]:
    """Load YAML file and validate each member with Pydantic."""
    with logger.contextualize(path=yaml_path, operation="load_yaml"):
        # Check file existence
        if not yaml_path.exists():
            logger.error("YAML file not found")
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")

        # Load YAML
        try:
            with yaml_path.open("r", encoding="utf-8") as f:
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
                raise ValueError(f"Member validation failed at index {i}: {e}") from e

        if not validated_members:
            logger.warning("No valid members found in YAML file")

        logger.info(
            "Successfully loaded and validated members", count=len(validated_members)
        )
        return validated_members


def reload_member_data(
    yaml_path: Path,
) -> tuple[dict[str, MemberInDB], list[MemberInDB]]:
    """Reload member data and return both dict and list representations."""
    with logger.contextualize(operation="reload_data"):
        logger.info("Reloading member data from YAML")

        # Load and validate
        members = load_and_validate_yaml(yaml_path)

        # Create both storage formats
        members_dict = {m.memberid: m for m in members}
        members_list = members.copy()

        logger.info(
            "Member data reload completed",
            count=len(members),
            member_ids=[m.memberid for m in members[:5]],  # Log first 5 IDs
        )

        return members_dict, members_list
