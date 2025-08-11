"""Tests for MemberRepository class."""

# ruff : noqa f841
from pathlib import Path

import pytest
from app.feature.member.rep_member import MemberRepository
from app.feature.member.sch_member import MemberInDB

# =============================================================================
# UNIT TESTS - Constructor & Initialization
# =============================================================================


@pytest.mark.unit
class TestMemberRepositoryInitialization:
    """Test repository initialization and constructor."""

    def test_init_with_default_path_should_use_data_members_yaml(self, mocker):
        """Test default file path when none provided."""
        # Arrange
        mock_load = mocker.patch.object(
            MemberRepository, "_load_data_from_file", return_value=[]
        )

        # Act
        repo = MemberRepository()

        # Assert
        assert repo.file_path == Path("data/members.yaml")
        mock_load.assert_called_once()

    def test_init_with_custom_path_should_use_provided_path(self, mocker):
        """Test custom file path initialization."""
        # Arrange
        custom_path = Path("custom/path/members.yaml")
        mock_load = mocker.patch.object(
            MemberRepository, "_load_data_from_file", return_value=[]
        )

        # Act
        repo = MemberRepository(custom_path)

        # Assert
        assert repo.file_path == custom_path
        mock_load.assert_called_once()

    def test_init_with_string_path_should_convert_to_path(self, mocker):
        """Test string path gets converted to Path object."""
        # Arrange
        path_string = "test/members.yaml"
        mock_load = mocker.patch.object(
            MemberRepository, "_load_data_from_file", return_value=[]
        )

        # Act
        repo = MemberRepository(path_string)

        # Assert
        assert repo.file_path == Path(path_string)
        assert isinstance(repo.file_path, Path)

    def test_init_should_call_reload(self, mocker):
        """Test that initialization calls reload."""
        # Arrange
        mock_reload = mocker.patch.object(MemberRepository, "reload")

        # Act
        MemberRepository()

        # Assert
        mock_reload.assert_called_once()


# =============================================================================
# UNIT TESTS - Core Repository Methods
# =============================================================================


@pytest.mark.unit
class TestMemberRepositoryCoreMethods:
    """Test core repository functionality."""

    def test_get_member_by_id_existing_member_should_return_member(
        self, sample_member_db_data, mocker
    ):
        """Test getting existing member by ID."""
        # Arrange
        member = MemberInDB(**sample_member_db_data)
        mock_load = mocker.patch.object(
            MemberRepository, "_load_data_from_file", return_value=[member]
        )
        repo = MemberRepository()

        # Act
        result = repo.get_member_by_id(member.memberid)

        # Assert
        assert result == member
        assert result.memberid == member.memberid  # pyright: ignore[reportOptionalMemberAccess]

    def test_get_member_by_id_nonexistent_member_should_return_none(self, mocker):
        """Test getting non-existent member returns None."""
        # Arrange
        mock_load = mocker.patch.object(
            MemberRepository, "_load_data_from_file", return_value=[]
        )
        repo = MemberRepository()

        # Act
        result = repo.get_member_by_id("NONEXISTENT")

        # Assert
        assert result is None

    def test_get_all_members_should_return_copy_of_members(
        self, sample_member_db_data, mocker
    ):
        """Test get_all_members returns a copy."""
        # Arrange
        members = [MemberInDB(**sample_member_db_data)]
        mock_load = mocker.patch.object(
            MemberRepository, "_load_data_from_file", return_value=members
        )
        repo = MemberRepository()

        # Act
        result = repo.get_all_members()

        # Assert
        assert result == members
        assert result is not repo._members  # Should be a copy

    def test_get_member_count_should_return_correct_count(
        self, sample_member_db_data, mocker
    ):
        """Test member count calculation."""
        # Arrange
        members = [MemberInDB(**sample_member_db_data)]
        mock_load = mocker.patch.object(
            MemberRepository, "_load_data_from_file", return_value=members
        )
        repo = MemberRepository()

        # Act
        count = repo.get_member_count()

        # Assert
        assert count == 1

    def test_has_member_existing_should_return_true(
        self, sample_member_db_data, mocker
    ):
        """Test has_member with existing member."""
        # Arrange
        member = MemberInDB(**sample_member_db_data)
        mock_load = mocker.patch.object(
            MemberRepository, "_load_data_from_file", return_value=[member]
        )
        repo = MemberRepository()

        # Act
        result = repo.has_member(member.memberid)

        # Assert
        assert result is True

    def test_has_member_nonexistent_should_return_false(self, mocker):
        """Test has_member with non-existent member."""
        # Arrange
        mock_load = mocker.patch.object(
            MemberRepository, "_load_data_from_file", return_value=[]
        )
        repo = MemberRepository()

        # Act
        result = repo.has_member("NONEXISTENT")

        # Assert
        assert result is False

    def test_is_member_active_active_member_should_return_true(
        self, sample_member_db_data, mocker
    ):
        """Test is_member_active with active member."""
        # Arrange
        member_data = sample_member_db_data.copy()
        member_data["is_active"] = True
        member = MemberInDB(**member_data)
        mock_load = mocker.patch.object(
            MemberRepository, "_load_data_from_file", return_value=[member]
        )
        repo = MemberRepository()

        # Act
        result = repo.is_member_active(member.memberid)

        # Assert
        assert result is True

    def test_is_member_active_inactive_member_should_return_false(
        self, sample_member_db_data, mocker
    ):
        """Test is_member_active with inactive member."""
        # Arrange
        member_data = sample_member_db_data.copy()
        member_data["is_active"] = False
        member = MemberInDB(**member_data)
        mock_load = mocker.patch.object(
            MemberRepository, "_load_data_from_file", return_value=[member]
        )
        repo = MemberRepository()

        # Act
        result = repo.is_member_active(member.memberid)

        # Assert
        assert result is False

    def test_is_member_active_nonexistent_member_should_return_false(self, mocker):
        """Test is_member_active with non-existent member."""
        # Arrange
        mock_load = mocker.patch.object(
            MemberRepository, "_load_data_from_file", return_value=[]
        )
        repo = MemberRepository()

        # Act
        result = repo.is_member_active("NONEXISTENT")

        # Assert
        assert result is False

    def test_check_allow_nosign_allowed_should_return_true(
        self, sample_member_db_data, mocker
    ):
        """Test check_allow_nosign with member that allows no signature."""
        # Arrange
        member_data = sample_member_db_data.copy()
        member_data["allow_nosign"] = True
        member = MemberInDB(**member_data)
        mock_load = mocker.patch.object(
            MemberRepository, "_load_data_from_file", return_value=[member]
        )
        repo = MemberRepository()

        # Act
        result = repo.check_allow_nosign(member.memberid)

        # Assert
        assert result is True

    def test_check_allow_nosign_not_allowed_should_return_false(
        self, sample_member_db_data, mocker
    ):
        """Test check_allow_nosign with member that requires signature."""
        # Arrange
        member_data = sample_member_db_data.copy()
        member_data["allow_nosign"] = False
        member = MemberInDB(**member_data)
        mock_load = mocker.patch.object(
            MemberRepository, "_load_data_from_file", return_value=[member]
        )
        repo = MemberRepository()

        # Act
        result = repo.check_allow_nosign(member.memberid)

        # Assert
        assert result is False

    def test_get_member_ids_should_return_all_ids(self, sample_member_db_data, mocker):
        """Test getting all member IDs."""
        # Arrange
        members = [MemberInDB(**sample_member_db_data)]
        expected_ids = [m.memberid for m in members]
        mock_load = mocker.patch.object(
            MemberRepository, "_load_data_from_file", return_value=members
        )
        repo = MemberRepository()

        # Act
        result = repo.get_member_ids()

        # Assert
        assert set(result) == set(expected_ids)

    def test_clear_data_should_empty_repository(self, sample_member_db_data, mocker):
        """Test clearing repository data."""
        # Arrange
        members = [MemberInDB(**sample_member_db_data)]
        mock_load = mocker.patch.object(
            MemberRepository, "_load_data_from_file", return_value=members
        )
        repo = MemberRepository()
        assert repo.get_member_count() > 0  # Verify data exists

        # Act
        repo.clear_data()

        # Assert
        assert repo.get_member_count() == 0
        assert repo.get_all_members() == []
        assert repo.get_member_ids() == []


# =============================================================================
# UNIT TESTS - Reload & Error Handling
# =============================================================================


@pytest.mark.unit
class TestMemberRepositoryReload:
    """Test reload functionality and error handling."""

    def test_reload_success_should_update_data(self, sample_member_db_data, mocker):
        """Test successful reload updates repository data."""
        # Arrange
        old_members = [MemberInDB(**sample_member_db_data)]
        new_members = [MemberInDB(**sample_member_db_data)]

        mock_load = mocker.patch.object(MemberRepository, "_load_data_from_file")
        mock_load.side_effect = [old_members, new_members]  # First call, then reload

        repo = MemberRepository()
        assert repo.get_member_count() == 1

        # Act
        repo.reload()

        # Assert
        assert repo.get_member_count() == 1
        assert mock_load.call_count == 2

    def test_reload_failure_should_keep_existing_data(
        self, sample_member_db_data, mocker
    ):
        """Test reload failure preserves existing data (fallback behavior)."""
        # Arrange
        existing_members = [MemberInDB(**sample_member_db_data)]
        mock_load = mocker.patch.object(MemberRepository, "_load_data_from_file")
        mock_load.side_effect = [existing_members, Exception("Reload failed")]

        repo = MemberRepository()
        original_count = repo.get_member_count()
        original_members = repo.get_all_members()

        # Act
        repo.reload()  # Should not raise exception due to fallback

        # Assert
        assert repo.get_member_count() == original_count
        assert repo.get_all_members() == original_members

    def test_load_data_from_file_delegates_to_srv_memberdata(self, mocker):
        """Test that _load_data_from_file delegates to load_and_validate_yaml."""
        # Arrange
        valid_member_data = {
            "memberid": "M00001",
            "name": "Test User",
            "pin": "123456",
            "password": "abcdef",
            "is_active": True,
            "ipaddress": "192.168.1.1",
            "report_url": "http://example.com/report",
            "allow_nosign": False,
        }
        expected_members = [MemberInDB(**valid_member_data)]
        mock_load_yaml = mocker.patch(
            "app.feature.member.rep_member.load_and_validate_yaml"
        )
        mock_load_yaml.return_value = expected_members

        repo = MemberRepository()

        # Act
        result = repo._load_data_from_file()

        # Assert
        assert result == expected_members
        mock_load_yaml.assert_called_with(repo.file_path)


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


@pytest.mark.integration
class TestMemberRepositoryIntegration:
    """Integration tests with real file I/O."""

    def test_load_from_sample_yaml_file(self, sample_members_yaml_path):
        """Test loading from sample YAML file."""
        # Act
        repo = MemberRepository(sample_members_yaml_path)

        # Assert
        assert repo.get_member_count() >= 1
        members = repo.get_all_members()
        assert all(isinstance(m, MemberInDB) for m in members)
        assert all(len(m.memberid) >= 5 for m in members)

    def test_repository_with_nonexistent_file_should_raise_error(self, tmp_path):
        """Test repository initialization with non-existent file."""
        # Arrange
        nonexistent_path = tmp_path / "nonexistent.yaml"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            MemberRepository(nonexistent_path)

    def test_repository_end_to_end_workflow(self, tmp_path, sample_member_db_data):
        """Test complete repository workflow."""
        # Arrange
        yaml_content = f"""
members:
  - memberid: {sample_member_db_data["memberid"]}
    name: {sample_member_db_data["name"]}
    pin: "{sample_member_db_data["pin"]}"
    password: {sample_member_db_data["password"]}
    is_active: {sample_member_db_data["is_active"]}
    ipaddress: {sample_member_db_data["ipaddress"]}
    report_url: {sample_member_db_data["report_url"]}
    allow_nosign: {sample_member_db_data["allow_nosign"]}
"""
        yaml_file = tmp_path / "test_members.yaml"
        yaml_file.write_text(yaml_content, encoding="utf-8")

        # Act
        repo = MemberRepository(yaml_file)

        # Assert - Test all major operations
        assert repo.get_member_count() == 1

        member = repo.get_member_by_id(sample_member_db_data["memberid"])
        assert member is not None
        assert member.name == sample_member_db_data["name"]

        assert repo.has_member(sample_member_db_data["memberid"])
        assert not repo.has_member("NONEXISTENT")

        assert (
            repo.is_member_active(sample_member_db_data["memberid"])
            == sample_member_db_data["is_active"]
        )
        assert (
            repo.check_allow_nosign(sample_member_db_data["memberid"])
            == sample_member_db_data["allow_nosign"]
        )


# =============================================================================
# SMOKE TESTS
# =============================================================================


@pytest.mark.smoke
class TestMemberRepositorySmoke:
    """Smoke tests for basic functionality."""

    def test_repository_instantiation(self, mocker):
        """Test basic repository instantiation."""
        # Arrange
        mock_load = mocker.patch.object(
            MemberRepository, "_load_data_from_file", return_value=[]
        )

        # Act
        repo = MemberRepository()

        # Assert
        assert repo is not None
        assert hasattr(repo, "file_path")
        assert hasattr(repo, "_members")
        assert hasattr(repo, "_members_dict")

    def test_repository_basic_operations_with_empty_data(self, mocker):
        """Test repository works with empty data."""
        # Arrange
        mock_load = mocker.patch.object(
            MemberRepository, "_load_data_from_file", return_value=[]
        )
        repo = MemberRepository()

        # Act & Assert
        assert repo.get_member_count() == 0
        assert repo.get_all_members() == []
        assert repo.get_member_by_id("ANY") is None
        assert not repo.has_member("ANY")
        assert not repo.is_member_active("ANY")
        assert not repo.check_allow_nosign("ANY")
        assert repo.get_member_ids() == []
