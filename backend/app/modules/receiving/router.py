"""M4 Material Receiving (Sub-con Inward) — see architecture doc Section 5.2.
TODO: implement real endpoints; this placeholder confirms the module is
wired into the app and reachable."""

from fastapi import APIRouter

router = APIRouter(prefix="/receiving", tags=["receiving"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "M4 Material Receiving (Sub-con Inward)", "status": "not_yet_implemented"}
