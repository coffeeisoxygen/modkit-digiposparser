from enum import StrEnum


class DigiposCategory(StrEnum):
    """Kategori yang valid untuk endpoint list paket Digipos."""

    DATA = "DATA"
    VOICE_SMS = "VOICE_SMS"
    DIGITAL_OTHER = "DIGITAL_OTHER"
    DIGITAL_MUSIC = "DIGITAL_MUSIC"
    DIGITAL_GAME = "DIGITAL_GAME"
    ROAMING = "ROAMING"
    VF = "VF"
    BYU = "BYU"
    HVC_DATA = "HVC_DATA"
    HVC_VOICE_SMS = "HVC_VOICE_SMS"


class DigiposPaymentEnum(StrEnum):
    """Enum for allowed payment methods."""

    LINKAJA = "LINKAJA"
    NGRS = "NGRS"

