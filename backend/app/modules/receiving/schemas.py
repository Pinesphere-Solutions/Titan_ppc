"""Pydantic request/response schemas for the Gate Entry and Sub-con
Receiving floor kiosk stations, and M4 Material Receiving categorization
(architecture doc Section 5.1)."""

from pydantic import BaseModel


class ScanRequest(BaseModel):
    dc_no: str


class ScanResponse(BaseModel):
    dc_no: str
    vendor_name: str
    message: str


class CategorizeRequest(BaseModel):
    category: str  # "regular" | "rework"


class CategorizeResponse(BaseModel):
    dc_no: str
    vendor_name: str
    receiving_category: str
    message: str


class ReceivingListItem(BaseModel):
    dc_no: str
    vendor_name: str
    material_code: str
    receiving_category: str | None = None