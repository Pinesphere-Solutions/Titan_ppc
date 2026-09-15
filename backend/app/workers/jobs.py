"""Scheduled job bodies — registered in app/workers/scheduler.py.

sap_sync_job now runs the same map_dispatched_material() logic that the
manual /sap-outward/sync endpoint uses — the two share identical mapping
and validation behavior, just different triggers (schedule vs. on-demand
HTTP call). This is intentional: the manual endpoint stays useful for
testing/debugging even after automation is in place.
"""

from app.core.database import AsyncSessionLocal
from app.integrations.sap.dependency import get_sap_client
from app.integrations.sap.mapping import (
    SAPMappingError,
    map_dispatched_material,
    map_movement,
)


async def sap_sync_job() -> None:
    """Periodically pull dispatched material data AND movement records
    (101/313/321) from SAP, map/validate each, and upsert into the
    database. Movements run second since they depend on the
    DeliveryChallan records materials sync creates. See Titan SAP Data
    Mapping Module design doc, Sections 6 and 8.

    Uses its own database session (rather than a request-scoped one from
    get_db, since there's no HTTP request here) — this is the standard
    pattern for background jobs with SQLAlchemy's async session pattern.
    """
    sap_client = get_sap_client()

    # --- Dispatched materials first (movements depend on the DCs these create) ---
    materials = await sap_client.fetch_dispatched_materials()
    materials_succeeded = 0
    materials_failed = 0

    async with AsyncSessionLocal() as db:
        for record in materials:
            try:
                await map_dispatched_material(db, record)
                await db.commit()
                materials_succeeded += 1
            except SAPMappingError as e:
                await db.rollback()
                materials_failed += 1
                print(f"[sap_sync_job] material record failed: {record.get('sap_document_no', 'unknown')} — {e}")

    # --- Movements second ---
    movements = await sap_client.fetch_movements()
    movements_succeeded = 0
    movements_failed = 0

    async with AsyncSessionLocal() as db:
        for record in movements:
            try:
                await map_movement(db, record)
                await db.commit()
                movements_succeeded += 1
            except SAPMappingError as e:
                await db.rollback()
                movements_failed += 1
                print(
                    f"[sap_sync_job] movement record failed: "
                    f"{record.get('material_document_no', 'unknown')} — {e}"
                )

    print(
        f"[sap_sync_job] sync complete: materials {materials_succeeded} succeeded / "
        f"{materials_failed} failed ({len(materials)} total); "
        f"movements {movements_succeeded} succeeded / {movements_failed} failed ({len(movements)} total)"
    )


async def kpi_refresh_job() -> None:
    """Recompute dashboard KPI counts and refresh the cache.
    See architecture doc Section 5.4."""
    # TODO: run the KPI aggregation queries and write results to cache.
    print("[kpi_refresh_job] refreshed dashboard KPI cache")