"""M10 PPC Collection and Verification — see architecture doc Section 5.2.
TODO: implement real endpoints; this placeholder confirms the module is
wired into the app and reachable."""

from fastapi import APIRouter

router = APIRouter(prefix="/ppc-collection", tags=["ppc_collection"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "M10 PPC Collection and Verification", "status": "not_yet_implemented"}
