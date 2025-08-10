import pytest
from app.member.rep_member import MemberRepository


def test_load_members(sample_members_yaml_path):
    repo = MemberRepository(yaml_path=sample_members_yaml_path)
    assert len(repo.list_members()) == 2
    assert repo.get_member_by_id("otomax1").memberid == "otomax1"  # type: ignore


def test_get_member_by_id(sample_members_yaml_path):
    repo = MemberRepository(yaml_path=sample_members_yaml_path)
    member = repo.get_member_by_id("otomax2")
    assert member is not None
    assert member.memberid == "otomax2"
    assert repo.get_member_by_id("notfound") is None


def test_list_members(sample_members_yaml_path):
    repo = MemberRepository(yaml_path=sample_members_yaml_path)
    members = repo.list_members()
    assert isinstance(members, list)
    assert len(members) == 2


def test_check_allow_nosign(sample_members_yaml_path):
    repo = MemberRepository(yaml_path=sample_members_yaml_path)
    assert repo.check_allow_nosign("otomax1") is False
    assert repo.check_allow_nosign("otomax2") is True
    assert repo.check_allow_nosign("notfound") is False


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        MemberRepository(yaml_path="not_exist.yaml")


def test_empty_yaml(tmp_path):
    empty_yaml = tmp_path / "empty.yaml"
    empty_yaml.write_text("")
    repo = MemberRepository(yaml_path=str(empty_yaml))
    assert repo.list_members() == []


def test_malformed_yaml(tmp_path):
    malformed_yaml = tmp_path / "malformed.yaml"
    malformed_yaml.write_text("not: valid: yaml: [")
    with pytest.raises(Exception):
        MemberRepository(yaml_path=str(malformed_yaml))


def test_duplicate_member_ids(tmp_path):
    dup_yaml = tmp_path / "dup.yaml"
    dup_yaml.write_text("""
    - memberid: otomax1
      allow_nosign: false
    - memberid: otomax1
      allow_nosign: true
    """)
    repo = MemberRepository(yaml_path=str(dup_yaml))
    members = repo.list_members()
    ids = [m.memberid for m in members]
    assert ids.count("otomax1") == 2


def test_missing_required_fields(tmp_path):
    missing_yaml = tmp_path / "missing.yaml"
    missing_yaml.write_text("""
    - memberid: otomax3
    """)
    repo = MemberRepository(yaml_path=str(missing_yaml))
    member = repo.get_member_by_id("otomax3")
    # allow_nosign should default or error depending on model
    assert hasattr(member, "memberid")
    # If allow_nosign is required, this may raise or be None/False
