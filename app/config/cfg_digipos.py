"""condifg for digipos accoount / modules."""

from pydantic import BaseModel


class DigiposCoreConfig(BaseModel):
    API_BASEURL: str
    API_METHOD: str
    API_TIMEOUT: int
    API_RETRIES: int
    API_RETRIES_SECONDS: int
    API_USERNAME: str
    API_PASSWORD: str
    API_PIN: str
    API_NAME: str


class DigiposRespConfig(BaseModel):
    DATA_EXCLUDE_SUBCATEGORY: list | None
    DATA_EXCLUDE_PRODUCTNAME: list | None
    DATA_EXCLUDE_QUOTA_METADATA: list | None
    HVCDATA_EXCLUDE_SUBCATEGORY: list | None
    HVCDATA_EXCLUDE_PRODUCTNAME: list | None
    HVCDATA_EXCLUDE_QUOTA_METADATA: list | None
    VOICE_SMS_EXCLUDE_SUBCATEGORY: list | None
    VOICE_SMS_EXCLUDE_PRODUCTNAME: list | None
    VOICE_SMS_EXCLUDE_QUOTA_METADATA: list | None
