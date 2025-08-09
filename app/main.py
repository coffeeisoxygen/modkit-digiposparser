import time
from typing import TYPE_CHECKING

import uvicorn

# Impor fungsi registrasi router
from app.router.rtr_register import register_routers
from fastapi import FastAPI, Request

if TYPE_CHECKING:
    from app._version import __version__
else:
    __version__ = "0.0_1.dev"

version = __version__


# Buat instance FastAPI
app = FastAPI(
    title="Modkit Digipos Parser",
    description="API untuk mem-parsing dan menjadi proxy ke API Digipos.",
    version=version,
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


register_routers(app)


@app.get("/", tags=["Status"])
async def read_root():
    """Endpoint utama untuk pengecekan status server."""
    return {"status": "ok", "version": version}


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
