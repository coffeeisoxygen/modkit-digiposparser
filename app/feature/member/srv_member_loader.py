from pathlib import Path
from typing import Any

import yaml
from app.feature.member.sch_member import MemberInDB
from loguru import logger
from pydantic import ValidationError


class MemberLoaderService:
    """Bertanggung jawab memuat dan memvalidasi data member dari file YAML."""

    def __init__(self, yaml_path: str | Path):
        self.yaml_path = Path(yaml_path)

    def load_members(self) -> list[MemberInDB]:
        """Membaca data member dari file YAML dan memvalidasinya menggunakan Pydantic."""
        # Mengikat path dan operasi ke logger untuk pesan log yang lebih informatif
        logger.bind(path=self.yaml_path, operation="load_members").info(
            "Memulai memuat data member."
        )

        if not self.yaml_path.exists():
            logger.error("File YAML tidak ditemukan: {path}", path=self.yaml_path)
            raise FileNotFoundError(f"File YAML tidak ditemukan: {self.yaml_path}")

        try:
            with self.yaml_path.open("r", encoding="utf-8") as f:
                data: Any = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error("Gagal memuat file YAML: {error}", error=e)
            raise ValueError(f"Gagal memuat file YAML: {e}") from e

        members_list = data.get("members", [])
        if not isinstance(members_list, list):
            logger.error("Struktur 'members' harus berupa list.")
            raise TypeError("Struktur 'members' harus berupa list.")

        validated_members: list[MemberInDB] = []
        for item in members_list:
            try:
                validated_members.append(MemberInDB(**item))
            except ValidationError as e:
                logger.error(
                    "Validasi data YAML gagal untuk item: {item}. Error: {error}",
                    item=item,
                    error=e,
                )
                raise ValueError(
                    f"Validasi data YAML gagal untuk item: {item}. Error: {e}"
                ) from e

        logger.info(
            "Berhasil memuat dan memvalidasi {count} member dari {path}",
            count=len(validated_members),
            path=self.yaml_path,
        )
        return validated_members
