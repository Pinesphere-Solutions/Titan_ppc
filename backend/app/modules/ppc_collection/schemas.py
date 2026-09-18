"""Pydantic request/response schemas for M10 PPC Collection and Verification.
Kept separate from ORM models — see architecture doc Section 5.2."""

from pydantic import BaseModel


class PpcCollectionRequest(BaseModel):
    tray_no: str


class PpcCollectionResponse(BaseModel):
    dc_no: str
    tray_no: str
    vendor_name: str
    verification_status: str
    collected_by: str
    message: str


class PpcCollectionListItem(BaseModel):
    dc_no: str
    vendor_name: str
    material_code: str
    model: str
    quantity: int
    ud_post_status: str
