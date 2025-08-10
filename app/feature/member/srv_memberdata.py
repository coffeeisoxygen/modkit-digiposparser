"""Member Data Services.

Pure utility functions for member data operations:
- Duplicate checking
- YAML loading and validation
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
    """Load YAML file and validate each member with Pydantic.

    Pure function that handles complete YAML loading pipeline:
    - File existence check
    - YAML parsing
    - Structure validation
    - Duplicate checking
    - Pydantic validation

    Args:
        yaml_path: Path to YAML file to load

    Returns:
        List of validated MemberInDB objects

    Raises:
        FileNotFoundError: If YAML file doesn't exist
        ValueError: If YAML structure is invalid or duplicates found
        ValidationError: If Pydantic validation fails
    """
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
