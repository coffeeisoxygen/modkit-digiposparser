"""Tests for srv_memberdata pure functions."""

import time

import pytest

from app.feature.member.sch_member import MemberInDB
from app.feature.member.srv_memberdata import (
    check_duplicate_memberids,
    load_and_validate_yaml,
)

# =============================================================================
# UNIT TESTS - check_duplicate_memberids()
# =============================================================================


@pytest.mark.unit
class TestCheckDuplicateMemberIds:
    """Test duplicate detection logic."""

    def test_no_duplicates_should_return_empty_list(self):
        """Test with unique memberids."""
        # Arrange
        members_data = [
            {"memberid": "MEMBER01"},
            {"memberid": "MEMBER02"},
            {"memberid": "MEMBER03"},
        ]

        # Act
        duplicates = check_duplicate_memberids(members_data)

        # Assert
        assert duplicates == []

    def test_single_duplicate_should_return_duplicate_id(self):
        """Test with one duplicate memberid."""
        # Arrange
        members_data = [
            {"memberid": "MEMBER01"},
            {"memberid": "MEMBER02"},
            {"memberid": "MEMBER01"},  # Duplicate
        ]

        # Act
        duplicates = check_duplicate_memberids(members_data)

        # Assert
        assert duplicates == ["MEMBER01"]

    def test_multiple_duplicates_should_return_all_duplicate_ids(self):
        """Test with multiple duplicate memberids."""
        # Arrange
        members_data = [
            {"memberid": "MEMBER01"},
            {"memberid": "MEMBER02"},
            {"memberid": "MEMBER01"},  # Duplicate
            {"memberid": "MEMBER03"},
            {"memberid": "MEMBER02"},  # Duplicate
            {"memberid": "MEMBER01"},  # Another duplicate
        ]

        # Act
        duplicates = check_duplicate_memberids(members_data)

        # Assert
        assert set(duplicates) == {"MEMBER01", "MEMBER02"}

    def test_empty_list_should_return_empty_list(self):
        """Test with empty members list."""
        # Arrange
        members_data = []

        # Act
        duplicates = check_duplicate_memberids(members_data)

        # Assert
        assert duplicates == []

    def test_missing_memberid_should_handle_gracefully(self):
        """Test with missing memberid key."""
        # Arrange
        members_data = [
            {"memberid": "MEMBER01"},
            {"name": "Member without ID"},  # Missing memberid
            {"memberid": "MEMBER02"},
        ]

        # Act
        duplicates = check_duplicate_memberids(members_data)

        # Assert
        assert duplicates == []  # None should be treated as unique


# =============================================================================
# UNIT TESTS - load_and_validate_yaml()
# =============================================================================


@pytest.mark.unit
class TestLoadAndValidateYaml:
    """Test YAML loading and validation logic."""

    def test_file_not_found_should_raise_error(self, tmp_path):
        """Test FileNotFoundError when file doesn't exist."""
        # Arrange
        non_existent_path = tmp_path / "nonexistent.yaml"

        # Act & Assert
        with pytest.raises(FileNotFoundError) as exc_info:
            load_and_validate_yaml(non_existent_path)
        assert "YAML file not found" in str(exc_info.value)

    def test_invalid_yaml_should_raise_error(self, tmp_path):
        """Test ValueError when YAML is malformed."""
        # Arrange
        yaml_file = tmp_path / "invalid.yaml"
        yaml_file.write_text("invalid: yaml: content: [unclosed", encoding="utf-8")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            load_and_validate_yaml(yaml_file)
        assert "Failed to parse YAML file" in str(exc_info.value)

    def test_missing_members_key_should_raise_error(self, tmp_path):
        """Test ValueError when 'members' key is missing."""
        # Arrange
        yaml_file = tmp_path / "no_members.yaml"
        yaml_file.write_text("other_key: value", encoding="utf-8")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            load_and_validate_yaml(yaml_file)
        assert "YAML must contain 'members' key" in str(exc_info.value)

    def test_members_not_list_should_raise_error(self, tmp_path):
        """Test TypeError when 'members' is not a list."""
        # Arrange
        yaml_file = tmp_path / "members_not_list.yaml"
        yaml_file.write_text("members: not_a_list", encoding="utf-8")

        # Act & Assert
        with pytest.raises(TypeError) as exc_info:
            load_and_validate_yaml(yaml_file)
        assert "'members' must be a list" in str(exc_info.value)

    def test_duplicate_memberids_should_raise_error(self, tmp_path):
        """Test ValueError when duplicate memberids exist."""
        # Arrange
        yaml_content = """
members:
  - memberid: DUPLICATE01
    name: First Member
    pin: "123456"
    password: "password"
    ipaddress: "192.168.1.1"
    report_url: "http://example.com"
  - memberid: DUPLICATE01
    name: Second Member
    pin: "654321"
    password: "password2"
    ipaddress: "192.168.1.2"
    report_url: "http://example2.com"
"""
        yaml_file = tmp_path / "duplicates.yaml"
        yaml_file.write_text(yaml_content, encoding="utf-8")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            load_and_validate_yaml(yaml_file)
        assert "Duplicate memberids found" in str(exc_info.value)
        assert "DUPLICATE01" in str(exc_info.value)

    def test_invalid_member_data_should_raise_error(self, tmp_path):
        """Test ValueError when Pydantic validation fails."""
        # Arrange
        yaml_content = """
members:
  - memberid: INVALID
    name: Invalid Member
    pin: "123"  # Too short
    password: "pass"  # Too short
    ipaddress: "invalid_ip"  # Invalid IP
    report_url: "not_a_url"  # Invalid URL
"""
        yaml_file = tmp_path / "invalid_member.yaml"
        yaml_file.write_text(yaml_content, encoding="utf-8")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            load_and_validate_yaml(yaml_file)
        assert "Member validation failed" in str(exc_info.value)

    def test_valid_yaml_should_return_members(self, tmp_path, sample_member_db_data):
        """Test successful loading of valid YAML."""
        # Arrange
        yaml_content = f"""
members:
  - memberid: {sample_member_db_data[0]["memberid"]}
    name: {sample_member_db_data[0]["name"]}
    pin: "{sample_member_db_data[0]["pin"]}"
    password: {sample_member_db_data[0]["password"]}
    is_active: {sample_member_db_data[0]["is_active"]}
    ipaddress: {sample_member_db_data[0]["ipaddress"]}
    report_url: {sample_member_db_data[0]["report_url"]}
    allow_nosign: {sample_member_db_data[0]["allow_nosign"]}
"""
        yaml_file = tmp_path / "valid.yaml"
        yaml_file.write_text(yaml_content, encoding="utf-8")

        # Act
        members = load_and_validate_yaml(yaml_file)

        # Assert
        assert len(members) == 1
        assert isinstance(members[0], MemberInDB)
        assert members[0].memberid == sample_member_db_data[0]["memberid"]
        assert members[0].name == sample_member_db_data[0]["name"]

    def test_empty_members_list_should_return_empty_list(self, tmp_path):
        """Test with empty members list."""
        # Arrange
        yaml_content = "members: []"
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text(yaml_content, encoding="utf-8")

        # Act
        members = load_and_validate_yaml(yaml_file)

        # Assert
        assert members == []

    def test_multiple_valid_members_should_return_all(self, tmp_path):
        """Test loading multiple valid members."""
        # Arrange
        yaml_content = """
members:
  - memberid: MEMBER01
    name: First Member
    pin: "123456"
    password: "password1"
    is_active: true
    ipaddress: "192.168.1.1"
    report_url: "http://example1.com"
    allow_nosign: false
  - memberid: MEMBER02
    name: Second Member
    pin: "654321"
    password: "password2"
    is_active: false
    ipaddress: "192.168.1.2"
    report_url: "http://example2.com"
    allow_nosign: true
"""
        yaml_file = tmp_path / "multiple.yaml"
        yaml_file.write_text(yaml_content, encoding="utf-8")

        # Act
        members = load_and_validate_yaml(yaml_file)

        # Assert
        assert len(members) == 2
        assert all(isinstance(m, MemberInDB) for m in members)
        assert members[0].memberid == "MEMBER01"
        assert members[1].memberid == "MEMBER02"
        assert members[0].is_active is True
        assert members[1].is_active is False


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


@pytest.mark.integration
class TestSrvMemberdataIntegration:
    """Integration tests using conftest.py fixtures and real file I/O."""

    def test_load_sample_yaml_file(self, sample_members_yaml_path):
        """Test loading the sample YAML file from conftest.py."""
        # Act
        members = load_and_validate_yaml(sample_members_yaml_path)

        # Assert
        assert len(members) >= 1  # Should have at least one member
        assert all(isinstance(m, MemberInDB) for m in members)
        assert all(len(m.memberid) >= 5 for m in members)  # Min length validation

    @pytest.mark.parametrize(
        "member_data",
        [pytest.param(None, marks=pytest.mark.indirect)],
        indirect=["member_data"],
    )
    def test_validate_conftest_member_data(self, sample_member_db_data):
        """Test that conftest.py member data is valid."""
        # Act & Assert - should not raise any exception
        member = MemberInDB(**sample_member_db_data)
        assert member.memberid is not None
        assert len(member.memberid) >= 5


# =============================================================================
# PERFORMANCE TESTS
# =============================================================================


@pytest.mark.performance
class TestSrvMemberdataPerformance:
    """Performance tests for edge cases."""

    def test_large_duplicate_detection(self):
        """Test duplicate detection with large dataset."""
        # Arrange
        large_dataset = [{"memberid": f"MEMBER{i:05d}"} for i in range(10000)]
        large_dataset.append({"memberid": "MEMBER00001"})  # Add one duplicate

        # Act
        start_time = time.time()
        duplicates = check_duplicate_memberids(large_dataset)
        end_time = time.time()

        # Assert
        assert duplicates == ["MEMBER00001"]
        assert end_time - start_time < 1.0  # Should complete in under 1 second
