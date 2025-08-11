# Impor semua router Anda di sini
from app.router.admin.rtr_admin import router as admin_router
from app.router.digipos.list_handler import router as digipos_router
from fastapi import FastAPI


def register_routers(app: FastAPI):
    """Fungsi untuk mendaftarkan semua router ke aplikasi FastAPI utama."""
    # Daftarkan setiap router
    app.include_router(digipos_router)
    app.include_router(admin_router)

    # app.include_router(router_lain_jika_ada)
