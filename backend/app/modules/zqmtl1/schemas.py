"""Pydantic request/response schemas for M12 ZQMTL1 Processing.
Kept separate from ORM models — see architecture doc Section 5.2."""

from pydantic import BaseModel


class Zqmtl1PendingItem(BaseModel):
    dc_no: str
    vendor_name: str
    material_code: str
    model: str
    quantity: int


class Zqmtl1Response(BaseModel):
    dc_no: str
    vendor_name: str
    zqmtl1_status: str
    sap_status: str
    processed_by: str
    message: str
