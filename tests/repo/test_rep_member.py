import pytest
from app.member.rep_member import MemberRepository


@pytest.fixture
def sample_yaml():
    return """
members:
  - memberid: "abc123"
    allow_nosign: true
  - memberid: "def456"
    allow_nosign: false
"""


def test_load_members(tmp_path, sample_yaml):
    yaml_file = tmp_path / "members.yaml"
    yaml_file.write_text(sample_yaml)
    repo = MemberRepository(yaml_path=yaml_file)
    assert len(repo.list_members()) == 2
    assert repo.get_member_by_id("abc123").memberid == "abc123"  # type: ignore


def test_get_member_by_id(tmp_path, sample_yaml):
    yaml_file = tmp_path / "members.yaml"
    yaml_file.write_text(sample_yaml)
    repo = MemberRepository(yaml_path=yaml_file)
    member = repo.get_member_by_id("def456")
    assert member is not None
    assert member.memberid == "def456"
    assert repo.get_member_by_id("notfound") is None


def test_list_members(tmp_path, sample_yaml):
    yaml_file = tmp_path / "members.yaml"
    yaml_file.write_text(sample_yaml)
    repo = MemberRepository(yaml_path=yaml_file)
    members = repo.list_members()
    assert isinstance(members, list)
    assert len(members) == 2


def test_check_allow_nosign(tmp_path, sample_yaml):
    yaml_file = tmp_path / "members.yaml"
    yaml_file.write_text(sample_yaml)
    repo = MemberRepository(yaml_path=yaml_file)
    assert repo.check_allow_nosign("abc123") is True
    assert repo.check_allow_nosign("def456") is False
    assert repo.check_allow_nosign("notfound") is False


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        MemberRepository(yaml_path="not_exist.yaml")
