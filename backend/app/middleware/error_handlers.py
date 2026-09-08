"""Centralized exception handlers so SAP failures, validation failures,
and deviation states return a consistent error shape — architecture doc
Section 5.2."""

import httpx
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(httpx.HTTPError)
    async def sap_error_handler(request: Request, exc: httpx.HTTPError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                "error": "upstream_integration_error",
                "detail": "A downstream integration (SAP or mail) did not respond as expected.",
            },
        )
