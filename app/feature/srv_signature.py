"""OtomaX signature service."""

import base64
import hashlib
import hmac


class OtomaxSignatureService:
    """Service untuk generate dan verifikasi signature OtomaX API."""

    @staticmethod
    def generate_transaction_signature(
        memberid: str, product: str, dest: str, refid: str, pin: str, password: str
    ) -> str:
        """Generate OtomaX transaction signature.

        Algorithm:
            1. Build raw string: OtomaX|MEMBERID|PRODUCT|dest|refid|pin|password
               - memberid dan product diubah ke UPPERCASE
               - Field lain tetap original case
            2. SHA1 hash
            3. Base64 encode
            4. Hapus padding '='
            5. Replace '+' -> '-' dan '/' -> '_' (URL-safe)
        """
        # Build raw string
        raw = f"OtomaX|{memberid.upper()}|{product.upper()}|{dest}|{refid}|{pin}|{password}"

        # Generate SHA1 digest
        sha1_digest = hashlib.sha1(raw.encode()).digest()

        # Base64 encode dan URL-safe
        signature = base64.b64encode(sha1_digest).decode().rstrip("=")
        signature = signature.replace("+", "-").replace("/", "_")

        return signature

    @staticmethod
    def verify_signature(expected_data: dict, received_signature: str) -> bool:
        """Verifikasi signature secara timing-attack safe."""
        expected_signature = OtomaxSignatureService.generate_transaction_signature(
            **expected_data
        )
        return hmac.compare_digest(str(received_signature), str(expected_signature))


# Note: The following methods are commented out because they are not needed in the current context.

# commented out karena ngga butuh aja sih
# @staticmethod
# def generate_balance_check_signature(memberid: str, pin: str, password: str) -> str:
#     """Generate signature for balance check.

#     Args:
#         memberid: Member ID (will be converted to UPPERCASE)
#         pin: Member PIN (original case)
#         password: Member password (original case)

#     Returns:
#         str: Base64 encoded signature with URL-safe characters

#     Algorithm:
#         Raw string: OtomaX|CheckBalance|MEMBERID|pin|password
#     """
#     raw = f"OtomaX|CheckBalance|{memberid.upper()}|{pin}|{password}"
#     sha1_digest = hashlib.sha1(raw.encode()).digest()
#     signature = base64.b64encode(sha1_digest).decode().rstrip("=")
#     signature = signature.replace("+", "-").replace("/", "_")
#     return signature

# @staticmethod
# def generate_deposit_ticket_signature(
#     memberid: str, pin: str, password: str, amount: str
# ) -> str:
#     """Generate signature for deposit ticket.

#     Args:
#         memberid: Member ID (will be converted to UPPERCASE)
#         pin: Member PIN (original case)
#         password: Member password (original case)
#         amount: Deposit amount (original case)

#     Returns:
#         str: Base64 encoded signature with URL-safe characters

#     Algorithm:
#         Raw string: OtomaX|ticket|MEMBERID|pin|password|amount
#     """
#     raw = f"OtomaX|ticket|{memberid.upper()}|{pin}|{password}|{amount}"
#     sha1_digest = hashlib.sha1(raw.encode()).digest()
#     signature = base64.b64encode(sha1_digest).decode().rstrip("=")
#     signature = signature.replace("+", "-").replace("/", "_")
#     return signature
