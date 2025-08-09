"""Base Request dan Params Untuk Endpoint Digipos."""

from app.schemas.digipos.sch_enums import DigiposCategory, DigiposPaymentEnum
from pydantic import BaseModel, Field


class DigiposBaseConfig(BaseModel):
    model_config = {"populate_by_name": True}


class DigiposBaseRequest(DigiposBaseConfig):
    to: str
    category: DigiposCategory
    payment_method: DigiposPaymentEnum
    mark_json: int = Field(default=1, alias="json")


class DigiposListPaketRequest(DigiposBaseRequest):
    kolom: list[str] = Field(default_factory=list)
    subcategory: str | None = None
    duration: int | None = None
    up_harga: int | None = None


class DigiposBuyPacketRequest(DigiposBaseRequest):
    pin: int
    productid: int | str
    check: int | None = None
