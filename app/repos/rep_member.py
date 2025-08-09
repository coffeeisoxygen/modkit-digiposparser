from pathlib import Path

import yaml
from app.member.sch_member import MemberInDB


class MemberRepository:
    def __init__(self, yaml_path: str | Path = "members.yaml"):
        self.yaml_path = Path(yaml_path)
        self._members = self._load_members()

    def _load_members(self) -> list[MemberInDB]:
        with self.yaml_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        members = [MemberInDB(**item) for item in data.get("members", [])]
        return members

    def list_members(self) -> list[MemberInDB]:
        return self._members

    def get_member_by_id(self, memberid: str) -> MemberInDB | None:
        for member in self._members:
            if member.memberid == memberid:
                return member
        return None


# def main():
#     repo = MemberRepository(
#         "c:/Users/YOGA/project/otomax/modkit-digiposparser/members.yaml"
#     )
#     members = repo.list_members()
#     print(f"Loaded {len(members)} members")
#     for member in members:
#         print(member.model_dump())
#     # Validasi: cek apakah semua member punya 'memberid'
#     for member in members:
#         assert hasattr(member, "memberid"), "memberid missing in member"
#     print("All members validated.")


# if __name__ == "__main__":
#     main()
