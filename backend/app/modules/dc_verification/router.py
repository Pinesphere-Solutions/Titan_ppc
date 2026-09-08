"""M5 DC Verification — see architecture doc Section 5.2.
TODO: implement real endpoints; this placeholder confirms the module is
wired into the app and reachable."""

from fastapi import APIRouter

router = APIRouter(prefix="/dc-verification", tags=["dc_verification"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "M5 DC Verification", "status": "not_yet_implemented"}
