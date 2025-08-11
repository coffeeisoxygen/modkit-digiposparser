# import httpx

# # Impor Enum, Schema, dan Response Model kita
# from app.schemas.digipos import ClientResponse, DigiposCategory, DigiposListParams
# from fastapi import APIRouter, Depends, Response, status

# # --- Konfigurasi ---
# TARGET_API_BASE_URL = "http://10.0.0.3:10003"
# DEFAULT_USERNAME = "WIR6289504"
# DEFAULT_PAYMENT_METHOD = "LINKAJA"

# router = APIRouter(
#     prefix="/digipos",
#     tags=["Digipos"],
# )

# # =============================================================================
# # ENDPOINT DINAMIS TUNGGAL
# # =============================================================================

# # Kita definisikan response_model di sini untuk dokumentasi otomatis
# @router.get("/{category}/list", response_model=ClientResponse)
# async def get_list_by_category(
#     category: DigiposCategory,
#     params: DigiposListParams = Depends(),
#     # Parameter response untuk bisa mengubah status code
#     response: Response = Response(),
# ):
#     """Mendapatkan list paket berdasarkan kategori secara dinamis."""
#     query_params = params.model_dump(exclude_none=True)
#     target_params = {
#         "username": DEFAULT_USERNAME,
#         "payment_method": DEFAULT_PAYMENT_METHOD,
#         **query_params,
#         "category": category.value,
#     }
#     target_url = f"{TARGET_API_BASE_URL}/list_paket"

#     try:
#         async with httpx.AsyncClient() as client:
#             api_response = await client.get(target_url, params=target_params, timeout=10.0)
#             api_response.raise_for_status()

#             # --- Di sinilah PENTINGNYA PARSER nanti ---
#             # Saat ini kita hanya meneruskan data mentah.
#             # Nanti, Anda akan mem-parsing `api_response.json()`
#             # dan memasukkan hasilnya ke dalam field `data`.
#             parsed_data = api_response.json()

#             return ClientResponse(success=True, data=parsed_data)

#     except httpx.HTTPStatusError as e:
#         # Set status code di response FastAPI
#         response.status_code = status.HTTP_502_BAD_GATEWAY
#         error_message = f"API target mengembalikan error: {e.response.status_code}"
#         return ClientResponse(success=False, error=error_message, data=e.response.text)

#     except httpx.RequestError as e:
#         response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
#         error_message = f"Tidak dapat terhubung ke API target: {e}"
#         return ClientResponse(success=False, error=error_message)
