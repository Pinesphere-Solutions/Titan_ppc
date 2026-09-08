"""M2 Dashboard — see architecture doc Section 5.2.
TODO: implement real endpoints; this placeholder confirms the module is
wired into the app and reachable."""

from fastapi import APIRouter

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "M2 Dashboard", "status": "not_yet_implemented"}
