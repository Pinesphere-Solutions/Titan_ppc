
from typing import Any

import httpx

from app.core.config import settings
from app.integrations.sap.interface import SAPClientInterface

DEFAULT_TIMEOUT = httpx.Timeout(10.0, connect=5.0)


class SAPRestClient(SAPClientInterface):
    def __init__(self) -> None:
        if not settings.sap_base_url:
            raise RuntimeError("SAP_BASE_URL is not configured")
        self._client = httpx.AsyncClient(
            base_url=settings.sap_base_url,
            headers={"Authorization": f"Bearer {settings.sap_api_key}"},
            timeout=DEFAULT_TIMEOUT,
        )

    async def fetch_dispatched_materials(self) -> list[dict[str, Any]]:
        # TODO: confirm real endpoint path and response shape with SAP team.
        response = await self._client.get("/dispatched-materials")
        response.raise_for_status()
        return response.json()

    async def post_ud(self, dc_no: str, payload: dict[str, Any]) -> dict[str, Any]:
        # idempotency_key ensures a retried request after a timeout does not
        # result in a duplicate post — see architecture doc Section 5.2.
        headers = {"Idempotency-Key": f"ud-{dc_no}"}
        response = await self._client.post(f"/ud-post/{dc_no}", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    async def post_313(self, dc_no: str, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {"Idempotency-Key": f"sap313-{dc_no}"}
        response = await self._client.post(f"/sap-313/{dc_no}", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    async def aclose(self) -> None:
        await self._client.aclose()




    async def fetch_movements(self) -> list[dict[str, Any]]:
        # TODO: confirm real endpoint path and response shape with SAP team.
        response = await self._client.get("/movements")
        response.raise_for_status()
        return response.json()