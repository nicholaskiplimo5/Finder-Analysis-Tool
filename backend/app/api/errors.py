from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def install_error_handlers(app: FastAPI) -> None:
    """Every pure analysis function and service raises plain ValueError
    for bad input or insufficient data (unknown window sizes, a window
    too small to estimate a stat, etc.) -- map that to 400 in one place
    instead of a try/except in every route."""

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})
