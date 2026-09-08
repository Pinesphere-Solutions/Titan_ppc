"""M14 Reports — see architecture doc Section 5.2.
TODO: implement real endpoints; this placeholder confirms the module is
wired into the app and reachable."""

from fastapi import APIRouter

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "M14 Reports", "status": "not_yet_implemented"}
