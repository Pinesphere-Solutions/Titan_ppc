"""M7 Deviation Management — see architecture doc Section 5.2.
TODO: implement real endpoints; this placeholder confirms the module is
wired into the app and reachable."""

from fastapi import APIRouter

router = APIRouter(prefix="/deviations", tags=["deviations"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "M7 Deviation Management", "status": "not_yet_implemented"}
