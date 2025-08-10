from app.feature.member.sch_member import MemberInDB


class MemberRepository:
    """Menyediakan akses ke data member.

    Tidak bergantung pada sumber data (YAML, DB, dll.).
    """

    def __init__(self, members_data: list[MemberInDB]):
        # Mengubah list menjadi dict di memori untuk pencarian O(1)
        self._members: dict[str, MemberInDB] = {
            member.memberid: member for member in members_data
        }

    def get_member_by_id(self, memberid: str) -> MemberInDB | None:
        return self._members.get(memberid)

    def list_members(self) -> list[MemberInDB]:
        return list(self._members.values())

    def check_allow_nosign(self, memberid: str) -> bool:
        member = self.get_member_by_id(memberid)
        if member:
            return member.allow_nosign
        return False
