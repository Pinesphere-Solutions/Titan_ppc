"""Pydantic request/response schemas for M7 Deviation Management."""

from datetime import datetime

from pydantic import BaseModel


class DeviationItem(BaseModel):
    dc_no: str
    vendor_name: str
    material_code: str
    deviation_type: str
    expected_qty: int
    actual_qty: int
    difference_qty: int
    mail_status: str
    vendor_status: str
    resolved_by: str | None = None
    resolved_at: datetime | None = None
    created_at: datetime


class DeviationResolveResponse(BaseModel):
    dc_no: str
    vendor_status: str
    resolved_by: str
    resolved_at: datetime