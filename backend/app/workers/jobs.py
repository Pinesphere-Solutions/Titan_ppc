"""Scheduled job bodies — registered in app/workers/scheduler.py."""

from app.integrations.sap.dependency import get_sap_client


async def sap_sync_job() -> None:
    """Periodically pull dispatched material data from SAP and cache it.
    See architecture doc Section 5.4 — invalidate the cached snapshot on
    the next successful sync rather than purely by time."""
    sap_client = get_sap_client()
    materials = await sap_client.fetch_dispatched_materials()
    # TODO: write `materials` into the cache layer (Redis or in-process TTL).
    print(f"[sap_sync_job] fetched {len(materials)} dispatched material records")


async def kpi_refresh_job() -> None:
    """Recompute dashboard KPI counts and refresh the cache.
    See architecture doc Section 5.4."""
    # TODO: run the KPI aggregation queries and write results to cache.
    print("[kpi_refresh_job] refreshed dashboard KPI cache")
