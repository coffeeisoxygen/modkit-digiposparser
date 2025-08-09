"""condifg for digipos accoount / modules."""

from pydantic import BaseModel


class DigiposConfig(BaseModel):
    API_BASEURL: str
    API_METHOD: str
    API_TIMEOUT: int
    API_RETRIES: int
    API_RETRIES_SECONDS: int
    API_USERNAME: str
    API_PASSWORD: str
    API_PIN: str
    API_NAME: str
    RESPONSE_EXCLUDE_SUBCATEGORY: list[str]
    RESPONSE_EXCLUDE_PRODUCTNAME: list[str]
    RESPONSE_EXCLUDE_QUOTA_METADATA: list[str]
