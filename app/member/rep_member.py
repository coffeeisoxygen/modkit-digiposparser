from pathlib import Path

import yaml
from app.member.sch_member import MemberInDB


class MemberRepository:
    def __init__(self, yaml_path: str | Path = "members.yaml"):
        self.yaml_path = Path(yaml_path)
        self._members: dict[str, MemberInDB] = {}  # Dict for O(1) lookup
        self._load_members()

    def _load_members(self) -> None:
        if not self.yaml_path.exists():
            raise FileNotFoundError(f"Members file not found: {self.yaml_path}")

        with self.yaml_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        for item in data.get("members", []):
            member = MemberInDB(**item)
            self._members[member.memberid] = member  # Dict storage

    def get_member_by_id(self, memberid: str) -> MemberInDB | None:
        return self._members.get(memberid)  # O(1) lookup

    def list_members(self) -> list[MemberInDB]:
        return list(self._members.values())


def main():
    repo = MemberRepository(
        "c:/Users/YOGA/project/otomax/modkit-digiposparser/members.yaml"
    )
    members = repo.list_members()
    print(f"Loaded {len(members)} members")
    for member in members:
        print(member.model_dump())
    # Validasi: cek apakah semua member punya 'memberid'
    for member in members:
        assert hasattr(member, "memberid"), "memberid missing in member"
    print("All members validated.")


if __name__ == "__main__":
    main()
