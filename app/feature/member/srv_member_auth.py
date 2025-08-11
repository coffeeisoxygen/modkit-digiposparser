from typing import Protocol, runtime_checkable

from app.exceptions.custom.exc_member import (
    MemberAuthError,
    MemberInvalidCredentialsError,
    MemberInvalidSignatureError,
    MemberNotFoundError,
)
from app.feature.member.sch_member import MemberInDB, MemberTrxRequestModel
from app.feature.member.srv_signature import OtomaxSignatureService
from loguru import logger


@runtime_checkable
class MemberProvider(Protocol):
    def get_member_by_id(self, memberid: str) -> MemberInDB | None: ...


class MemberAuthService:
    """Layanan otentikasi member + verifikasi signature."""

    def __init__(self, member_manager: MemberProvider):
        self.member_manager = member_manager
        self.otomax_sign_service = OtomaxSignatureService()

    def authenticate_and_verify(self, request: MemberTrxRequestModel) -> MemberInDB:
        """Autentikasi member, cek status, dan validasi signature."""
        with logger.contextualize(memberid=request.memberid, op="auth_verify"):
            logger.info("Mulai autentikasi member")

            member_db = self._get_active_member(request.memberid)

            if request.sign:
                self._verify_signature(request, member_db)
            else:
                self._verify_without_signature(request, member_db)

            logger.info("Autentikasi sukses")
            return member_db

    def _get_active_member(self, memberid: str) -> MemberInDB:
        """Ambil member dari DB + cek aktif."""
        member = self.member_manager.get_member_by_id(memberid)
        if not member:
            raise MemberNotFoundError(f"Member ID '{memberid}' not found")
        if not member.is_active:
            raise MemberAuthError("Member tidak aktif")
        return member

    def _verify_without_signature(
        self, request: MemberTrxRequestModel, member_db: MemberInDB
    ):
        """Otentikasi menggunakan PIN atau Password (jika diizinkan)."""
        if not member_db.allow_nosign:
            raise MemberInvalidSignatureError("Signature wajib untuk member ini")

        if request.pin and str(request.pin) == member_db.pin.get_secret_value():
            logger.info("Otentikasi PIN sukses")
        elif (
            request.password
            and str(request.password) == member_db.password.get_secret_value()
        ):
            logger.info("Otentikasi Password sukses")
        else:
            raise MemberInvalidCredentialsError("PIN atau Password tidak valid")

    def _verify_signature(self, request: MemberTrxRequestModel, member_db: MemberInDB):
        """Verifikasi signature yang dikirim client (OtomaX format)."""
        expected_data = dict(
            memberid=request.memberid,
            product=str(request.product or ""),
            dest=str(request.dest or ""),
            refid=str(request.refid or ""),
            pin=member_db.pin.get_secret_value(),
            password=member_db.password.get_secret_value(),
        )

        logger.debug(f"Expected data: {expected_data}")
        logger.debug(f"Received signature: {request.sign}")

        verify_result = self.otomax_sign_service.verify_signature(
            expected_data, str(request.sign or "")
        )
        logger.debug(f"Verify result: {verify_result}")

        if not verify_result:
            expected_sig = self.otomax_sign_service.generate_transaction_signature(
                **expected_data
            )
            logger.error(
                "Signature tidak valid. Diterima={}, Diharapkan={}",
                request.sign,
                expected_sig,
            )
            raise MemberInvalidSignatureError("Signature tidak valid")

        logger.info("Signature valid")
