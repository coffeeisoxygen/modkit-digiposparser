# Member Authentication Service

from typing import Protocol, runtime_checkable

from app.exceptions.exc_member import (
    MemberAuthError,
    MemberInvalidCredentialsError,
    MemberInvalidSignatureError,
    MemberNotFoundError,
)
from app.feature.member.sch_member import MemberInDB
from app.feature.member.sch_memberauth import MemberTrxRequestModel
from app.feature.srv_signature import OtomaxSignatureService
from loguru import logger


@runtime_checkable
class MemberProvider(Protocol):
    """Protocol for member data providers (Manager, Repository, etc)."""

    def get_member_by_id(self, memberid: str) -> MemberInDB | None:
        """Get member by ID."""
        ...

    def is_member_active(self, memberid: str) -> bool:
        """Check if member is active."""
        ...

    def check_allow_nosign(self, memberid: str) -> bool:
        """Check if member allows nosign auth."""
        ...


class MemberAuthService:
    """Layanan yang mengurus otentikasi member dan validasi signature."""

    def __init__(self, member_manager: MemberProvider):
        self.member_manager = member_manager
        self.otomax_sign_service = OtomaxSignatureService()  # Direct instantiation

    def authenticate_and_verify(self, request: MemberTrxRequestModel) -> MemberInDB:
        """Melakukan otentikasi member, memeriksa status, dan memvalidasi signature."""
        with logger.contextualize(
            memberid=request.memberid, operation="authenticate_and_verify"
        ):
            logger.info("Memulai proses otentikasi.")

            # Langkah 1: Ambil data member dan cek status keaktifan
            member_db = self.member_manager.get_member_by_id(request.memberid)
            if not member_db:
                logger.warning("Percobaan otentikasi gagal: Member tidak ditemukan.")
                raise MemberNotFoundError(
                    message=f"Member ID '{request.memberid}' not found."
                )

            if not member_db.is_active:
                logger.warning("Percobaan otentikasi gagal: Member tidak aktif.")
                raise MemberAuthError(message="Member tidak aktif.")

            # Langkah 2: Logika bercabang utama untuk otentikasi
            if request.sign:
                # Prioritas verifikasi signature jika disediakan
                self._verify_signature(request, member_db)
                # Jika verifikasi berhasil, logika di bawah tidak akan dieksekusi
            else:
                # Opsi otentikasi tanpa signature
                if member_db.allow_nosign:
                    if (
                        request.pin
                        and str(request.pin) == member_db.pin.get_secret_value()
                    ):
                        logger.info("Otentikasi berhasil dengan PIN.")
                    elif (
                        request.password
                        and str(request.password)
                        == member_db.password.get_secret_value()
                    ):
                        logger.info("Otentikasi berhasil dengan Password.")
                    else:
                        logger.warning("PIN atau Password tidak valid.")
                        raise MemberInvalidCredentialsError(
                            message="PIN atau Password tidak valid."
                        )
                else:
                    logger.warning("Signature wajib, namun tidak ada di request.")
                    raise MemberInvalidSignatureError(
                        message="Signature wajib untuk member ini."
                    )

            logger.info("Otentikasi member berhasil.")
            return member_db

    def _verify_signature(self, request: MemberTrxRequestModel, member_db: MemberInDB):  # noqa: ARG002
        """Metode helper untuk memverifikasi signature."""
        # Validasi bahwa signature harus ada jika metode ini dipanggil
        if not request.sign:
            logger.warning("Panggilan verifikasi signature tanpa signature di request.")
            raise MemberInvalidSignatureError(message="Signature tidak ada di request.")

        expected_sign = self.otomax_sign_service.generate_transaction_signature(
            memberid=request.memberid,
            product=str(request.product) if request.product is not None else "",
            dest=str(request.refid)
            if request.refid is not None
            else "",  # Using refid as dest
            refid=str(request.refid) if request.refid is not None else "",
            pin=str(request.pin) if request.pin is not None else "",
            password=str(request.password) if request.password is not None else "",
        )

        if request.sign != expected_sign:
            logger.error(
                "Signature tidak valid. Diterima: {}, Diharapkan: {}",
                request.sign,
                expected_sign,
            )
            raise MemberInvalidSignatureError(message="Signature tidak valid.")

        logger.info("Signature berhasil diverifikasi.")
