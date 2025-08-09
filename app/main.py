from typing import TYPE_CHECKING

import uvicorn
from fastapi import FastAPI

if TYPE_CHECKING:
    from app._version import __version__
else:
    __version__ = "0.0_1.dev"  # or set a default/fallback value

version = __version__


app = FastAPI(
    title="Modkit Digipos Parser",
    description="API for parsing Digipos data",
    version=version,
)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
