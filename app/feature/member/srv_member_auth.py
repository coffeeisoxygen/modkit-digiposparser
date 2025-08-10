# Member Authentication Service

from app.exceptions.exc_member import (
    MemberAuthError,
    MemberInvalidCredentialsError,
    MemberInvalidSignatureError,
    MemberNotFoundError,
)
from app.feature.member.sch_member import MemberInDB
from app.feature.member.srv_member_manager import MemberManager
from app.feature.transaction.sch_request import ReqClientBase
from app.service.signature.srv_signature import OtomaxSignatureService
from loguru import logger


class MemberAuthService:
    """Layanan yang mengurus otentikasi member dan validasi signature."""

    def __init__(
        self,
        member_manager: MemberManager,
        otomax_sign_service: OtomaxSignatureService,
    ):
        self.member_manager = member_manager
        self.otomax_sign_service = otomax_sign_service

    def authenticate_and_verify(self, request: ReqClientBase) -> MemberInDB:
        """Melakukan otentikasi member, memeriksa status, dan memvalidasi signature."""
        with logger.contextualize(
            memberid=request.memberid, operation="authenticate_and_verify"
        ):
            logger.info("Memulai proses otentikasi.")

            # Langkah 1: Ambil data member dan cek status keaktifan
            member_db = self.member_manager.get_member(request.memberid)
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
                    if request.pin and request.pin == member_db.pin.get_secret_value():
                        logger.info("Otentikasi berhasil dengan PIN.")
                    elif (
                        request.password
                        and request.password == member_db.password.get_secret_value()
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

    def _verify_signature(self, request: ReqClientBase, member_db: MemberInDB):
        """Metode helper untuk memverifikasi signature."""
        # Validasi bahwa signature harus ada jika metode ini dipanggil
        if not request.sign:
            logger.warning("Panggilan verifikasi signature tanpa signature di request.")
            raise MemberInvalidSignatureError(message="Signature tidak ada di request.")

        expected_sign = self.otomax_sign_service.generate_transaction_signature(
            memberid=request.memberid,
            product=request.product,
            dest=request.dest,
            refid=request.refid if request.refid is not None else "",
            pin=request.pin if request.pin is not None else "",
            password=request.password if request.password is not None else "",
        )

        if request.sign != expected_sign:
            logger.error(
                "Signature tidak valid. Diterima: {}, Diharapkan: {}",
                request.sign,
                expected_sign,
            )
            raise MemberInvalidSignatureError(message="Signature tidak valid.")

        logger.info("Signature berhasil diverifikasi.")
