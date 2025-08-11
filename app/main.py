from typing import TYPE_CHECKING

import uvicorn
from app.custom.app_lifespan import lifespan
from app.custom.app_middleware import LoggingMiddleware

# Impor fungsi registrasi router
from app.exceptions.exc_base import JSONResponse
from app.router.rtr_register import register_routers
from app.service.token.srv_token import logger
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(
        f"Validation error: {exc.errors()} | Path: {request.url.path} | Method: {request.method}"
    )
    body = exc.body
    if isinstance(body, bytes):
        try:
            body = body.decode("utf-8")
        except Exception:
            body = str(body)
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": body},
    )


register_routers(app)


@app.get("/", tags=["Status"])
async def read_root():
    """Endpoint utama untuk pengecekan status server."""
    return {"status": "ok", "version": version}


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
