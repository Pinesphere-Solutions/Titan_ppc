"""In-memory mock SAP client for local development and testing — used
while the real SAP integration is unconfirmed/unreachable (architecture
doc Section 7.6). Lets M4–M13 be built and demoed end-to-end today."""

from typing import Any


class MockSAPClient:
    def __init__(self) -> None:
        self._posted_ud: dict[str, dict[str, Any]] = {}
        self._posted_313: dict[str, dict[str, Any]] = {}

    async def fetch_dispatched_materials(self) -> list[dict[str, Any]]:
        return [
            {
                "sap_document_no": "SAMPLE-0001",
                "dc_no": "DC-0001",
                "material_code": "MAT-001",
                "model": "MODEL-A",
                "vendor_name": "Sample Vendor",
                "quantity": 500,
                "dispatch_date": "2026-09-01",
            }
        ]

    async def post_ud(self, dc_no: str, payload: dict[str, Any]) -> dict[str, Any]:
        # Idempotent: repeated calls with the same dc_no return the same result.
        if dc_no not in self._posted_ud:
            self._posted_ud[dc_no] = {"dc_no": dc_no, "status": "posted", **payload}
        return self._posted_ud[dc_no]

    async def post_313(self, dc_no: str, payload: dict[str, Any]) -> dict[str, Any]:
        if dc_no not in self._posted_313:
            self._posted_313[dc_no] = {"dc_no": dc_no, "status": "posted", **payload}
        return self._posted_313[dc_no]

    async def aclose(self) -> None:
        return None
