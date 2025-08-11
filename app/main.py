from typing import TYPE_CHECKING

import uvicorn
from app.custom.app_lifespan import lifespan
from app.custom.app_middleware import LoggingMiddleware  # <-- import custom middleware

# Impor fungsi registrasi router
from app.router.rtr_register import register_routers
from fastapi import FastAPI

if TYPE_CHECKING:
    from app._version import __version__
else:
    __version__ = "0.0_1.dev"

version = __version__


app = FastAPI(
    title="Modkit Digipos Parser",
    description="API untuk mem-parsing dan menjadi proxy ke API Digipos.",
    version=version,
    lifespan=lifespan,
)

app.add_middleware(LoggingMiddleware)


register_routers(app)


@app.get("/", tags=["Status"])
async def read_root():
    """Endpoint utama untuk pengecekan status server."""
    return {"status": "ok", "version": version}


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
