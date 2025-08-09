import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

# --- Konfigurasi (spesifik untuk router ini) ---
TARGET_API_BASE_URL = "http://10.0.0.3:10003"
DEFAULT_USERNAME = "WIR6289504"
DEFAULT_PAYMENT_METHOD = "LINKAJA"

# Membuat instance APIRouter
router = APIRouter(
    prefix="/digipos",
    tags=["Digipos"],
)


# =============================================================================
# FUNGSI HELPER INTERNAL
# =============================================================================
async def _fetch_from_digipos(category: str, request: Request) -> JSONResponse:
    """Fungsi helper untuk membangun request dan mengambil data dari API Digipos."""
    incoming_params = dict(request.query_params)
    target_params = {
        "username": DEFAULT_USERNAME,
        "payment_method": DEFAULT_PAYMENT_METHOD,
        **incoming_params,
        "category": category,
    }
    target_url = f"{TARGET_API_BASE_URL}/list_paket"

    print(f"Menerjemahkan request ke: {target_url} dengan params: {target_params}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(target_url, params=target_params, timeout=10.0)
            response.raise_for_status()
            return JSONResponse(
                content=response.json(), status_code=response.status_code
            )
    except httpx.HTTPStatusError as e:
        return JSONResponse(
            content={
                "error": "API target mengembalikan error",
                "details": e.response.text,
            },
            status_code=e.response.status_code,
        )
    except httpx.RequestError as e:
        return JSONResponse(
            content={"error": "Tidak dapat terhubung ke API target", "details": str(e)},
            status_code=503,
        )


# =============================================================================
# ENDPOINT PUBLIK (relatif terhadap prefix /digipos)
# =============================================================================


@router.get("/data/list")
async def get_data_list(request: Request):
    """Mendapatkan list paket kategori 'DATA'."""
    return await _fetch_from_digipos("DATA", request)


@router.get("/voice-sms/list")
async def get_voice_sms_list(request: Request):
    """Mendapatkan list paket kategori 'VOICE_SMS'."""
    return await _fetch_from_digipos("VOICE_SMS", request)


@router.get("/digital-other/list")
async def get_digital_other_list(request: Request):
    """Mendapatkan list paket kategori 'DIGITAL_OTHER'."""
    return await _fetch_from_digipos("DIGITAL_OTHER", request)


@router.get("/digital-music/list")
async def get_digital_music_list(request: Request):
    """Mendapatkan list paket kategori 'DIGITAL_MUSIC'."""
    return await _fetch_from_digipos("DIGITAL_MUSIC", request)


@router.get("/digital-game/list")
async def get_digital_game_list(request: Request):
    """Mendapatkan list paket kategori 'DIGITAL_GAME'."""
    return await _fetch_from_digipos("DIGITAL_GAME", request)


@router.get("/roaming/list")
async def get_roaming_list(request: Request):
    """Mendapatkan list paket kategori 'ROAMING'."""
    return await _fetch_from_digipos("ROAMING", request)


@router.get("/vf/list")
async def get_vf_list(request: Request):
    """Mendapatkan list paket kategori 'VF'."""
    return await _fetch_from_digipos("VF", request)


@router.get("/byu/list")
async def get_byu_list(request: Request):
    """Mendapatkan list paket kategori 'BYU'."""
    return await _fetch_from_digipos("BYU", request)


@router.get("/hvc-data/list")
async def get_hvc_data_list(request: Request):
    """Mendapatkan list paket kategori 'HVC_DATA'."""
    return await _fetch_from_digipos("HVC_DATA", request)


@router.get("/hvc-voice-sms/list")
async def get_hvc_voice_sms_list(request: Request):
    """Mendapatkan list paket kategori 'HVC_VOICE_SMS'."""
    return await _fetch_from_digipos("HVC_VOICE_SMS", request)
