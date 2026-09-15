"""SAP-to-application mapping layer — see Titan SAP Data Mapping Module
design doc, Section 5 (mapping matrix) and Section 8 (processing flow).

This module deliberately covers ONLY the fields confirmed in that
document: DC Number, Line Item Count, Vendor Code/Name, Material Code,
Model, Quantity (Front/Back Case), Dispatch Date. PO Number/Line Item are
stored (since PO data was part of the original request) but NOT
validated as strictly as confirmed fields, since their exact SAP shape
is still [OPEN]. Movement-type mapping (101/313/321) is intentionally
NOT included here yet — see the design doc's recommendation to sequence
that separately once this simpler path is proven.
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dc_verification.models import DeliveryChallan
from app.modules.masters.models import Vendor
from app.modules.sap_outward.models import Dispatch
from app.modules.sap_processing.models import SapMovement


class SAPMappingError(Exception):
    """Raised when a SAP record fails validation before mapping.
    Callers should treat this as a permanent error (see design doc
    Section 10) — log it and route to manual review, don't retry blindly."""


def validate_dispatch_record(record: dict[str, Any]) -> None:
    """Validation per SAP mapping doc Section 7, for the fields already
    confirmed. Raises SAPMappingError on the first failure."""
    required_fields = ["dc_no", "vendor_code", "vendor_name", "material_code", "sap_document_no"]
    for field in required_fields:
        if not record.get(field):
            raise SAPMappingError(f"Missing required field: {field}")

    line_item_count = record.get("line_item_count")
    if line_item_count is not None and line_item_count > 13:
        # Confirmed business rule (architecture doc): max 13 line items per DC.
        # The split-into-multiple-DCs logic lives elsewhere; this layer just
        # refuses to silently accept a record that violates the rule.
        raise SAPMappingError(
            f"DC {record['dc_no']} has {line_item_count} line items, exceeding the 13-item limit"
        )


async def _get_or_create_vendor(db: AsyncSession, vendor_code: str, vendor_name: str) -> Vendor:
    """Duplicate/update handling per SAP mapping doc Section 11: unique
    key is vendor_code. If found, name is refreshed (SAP is source of
    truth for vendor name); if not found, a new Vendor is created."""
    result = await db.execute(select(Vendor).where(Vendor.code == vendor_code))
    vendor = result.scalar_one_or_none()
    if vendor is None:
        vendor = Vendor(code=vendor_code, name=vendor_name)
        db.add(vendor)
        await db.flush()  # assigns vendor.id without committing yet
    elif vendor.name != vendor_name:
        vendor.name = vendor_name
    return vendor


async def _get_or_create_dispatch(db: AsyncSession, record: dict[str, Any], vendor: Vendor) -> Dispatch:
    """Unique key: sap_document_no, per the proposed key in Section 11
    of the mapping doc. This is a straightforward insert-or-update —
    conflict handling for records already progressed past this stage is
    still [OPEN] and NOT implemented here (see Section 11)."""
    result = await db.execute(select(Dispatch).where(Dispatch.sap_document_no == record["sap_document_no"]))
    dispatch = result.scalar_one_or_none()

    fields = {
        "vendor_id": vendor.id,
        "material_code": record["material_code"],
        "model": record.get("model"),
        "quantity_front_case": record.get("quantity_front_case"),
        "quantity_back_case": record.get("quantity_back_case"),
        "dispatch_date": record.get("dispatch_date"),
        "po_number": record.get("po_number"),
        "po_line_item": record.get("po_line_item"),
        "po_quantity": record.get("po_quantity"),
    }

    if dispatch is None:
        dispatch = Dispatch(sap_document_no=record["sap_document_no"], **fields)
        db.add(dispatch)
        await db.flush()
    else:
        for key, value in fields.items():
            setattr(dispatch, key, value)
    return dispatch


async def _get_or_create_delivery_challan(
    db: AsyncSession, record: dict[str, Any], dispatch: Dispatch
) -> DeliveryChallan:
    """Unique key: dc_no, per the proposed key in Section 11."""
    result = await db.execute(select(DeliveryChallan).where(DeliveryChallan.dc_no == record["dc_no"]))
    dc = result.scalar_one_or_none()

    if dc is None:
        dc = DeliveryChallan(
            dispatch_id=dispatch.id,
            dc_no=record["dc_no"],
            line_item_count=record.get("line_item_count", 1),
        )
        db.add(dc)
    else:
        dc.line_item_count = record.get("line_item_count", dc.line_item_count)
        # Note: verification_status is intentionally NOT overwritten here —
        # that field is application-owned once set, per the field-ownership
        # question raised in Section 11 of the mapping doc.
    return dc


async def map_dispatched_material(db: AsyncSession, record: dict[str, Any]) -> DeliveryChallan:
    """Entry point: takes one raw SAP record (as returned by
    MockSAPClient.fetch_dispatched_materials()) and maps/validates/
    persists it through Vendor -> Dispatch -> DeliveryChallan.

    Follows the flow in SAP mapping doc Section 8: validate, then
    duplicate/existing check via unique key, then insert or update.
    Raises SAPMappingError on validation failure — callers should catch
    this and route to the error/retry flow (Section 10), not let it
    propagate as a raw exception.
    """
    validate_dispatch_record(record)

    vendor = await _get_or_create_vendor(db, record["vendor_code"], record["vendor_name"])
    dispatch = await _get_or_create_dispatch(db, record, vendor)
    delivery_challan = await _get_or_create_delivery_challan(db, record, dispatch)

    return delivery_challan


VALID_MOVEMENT_TYPES = {"101", "313", "321"}


def validate_movement_record(record: dict[str, Any]) -> None:
    """Validation for movement records (101/313/321) — see SAP mapping
    doc Section 3 and Section 7."""
    required_fields = ["material_document_no", "movement_type", "dc_no"]
    for field in required_fields:
        if not record.get(field):
            raise SAPMappingError(f"Missing required field: {field}")

    if record["movement_type"] not in VALID_MOVEMENT_TYPES:
        raise SAPMappingError(
            f"Unrecognized movement type '{record['movement_type']}' "
            f"(expected one of {sorted(VALID_MOVEMENT_TYPES)})"
        )


async def map_movement(db: AsyncSession, record: dict[str, Any]) -> SapMovement:
    """Entry point for movement records. Requires the referenced DC to
    already exist — a movement can't be linked to a delivery challan
    SAP hasn't told us about yet. Unique key: material_document_no
    (proposed in SAP mapping doc Section 11)."""
    validate_movement_record(record)

    dc_result = await db.execute(select(DeliveryChallan).where(DeliveryChallan.dc_no == record["dc_no"]))
    dc = dc_result.scalar_one_or_none()
    if dc is None:
        raise SAPMappingError(
            f"Movement references DC {record['dc_no']}, which doesn't exist yet — "
            "sync dispatched materials before movements"
        )

    result = await db.execute(
        select(SapMovement).where(SapMovement.material_document_no == record["material_document_no"])
    )
    movement = result.scalar_one_or_none()

    if movement is None:
        movement = SapMovement(
            dc_id=dc.id,
            material_document_no=record["material_document_no"],
            movement_type=record["movement_type"],
            posting_date=record.get("posting_date"),
        )
        db.add(movement)
    else:
        # Idempotent — same material_document_no, no change needed beyond
        # confirming posting_date if it was updated.
        movement.posting_date = record.get("posting_date", movement.posting_date)

    return movement