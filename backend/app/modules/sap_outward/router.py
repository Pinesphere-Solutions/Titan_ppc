"""M3 SAP Material Outward — see architecture doc Section 5.2.
TODO: implement real endpoints; this placeholder confirms the module is
wired into the app and reachable."""

from fastapi import APIRouter

router = APIRouter(prefix="/sap-outward", tags=["sap_outward"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "M3 SAP Material Outward", "status": "not_yet_implemented"}
