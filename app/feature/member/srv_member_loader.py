# File: src/services/yaml_loader_service.py

from pathlib import Path
from typing import Any

import yaml
from app.feature.member.sch_member import MemberInDB
from pydantic import ValidationError


class MemberLoaderService:
    """Bertanggung jawab memuat dan memvalidasi data member dari file YAML."""

    def __init__(self, yaml_path: str | Path):
        self.yaml_path = Path(yaml_path)

    def load_members(self) -> list[MemberInDB]:
        """Membaca data member dari file YAML dan memvalidasinya menggunakan Pydantic."""
        if not self.yaml_path.exists():
            raise FileNotFoundError(f"File YAML tidak ditemukan: {self.yaml_path}")

        try:
            with self.yaml_path.open("r", encoding="utf-8") as f:
                data: Any = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Gagal memuat file YAML: {e}")

        members_list = data.get("members", [])
        if not isinstance(members_list, list):
            raise ValueError("Struktur 'members' harus berupa list.")

        validated_members: list[MemberInDB] = []
        for item in members_list:
            try:
                validated_members.append(MemberInDB(**item))
            except ValidationError as e:
                raise ValueError(
                    f"Validasi data YAML gagal untuk item: {item}. Error: {e}"
                )

        return validated_members
