"""Pydantic request/response schemas for M6 Physical Verification."""

from pydantic import BaseModel


class PhysicalVerificationResponse(BaseModel):
    dc_no: str
    vendor_name: str
    physical_verification_status: str
    verified_by: str
    message: str


class PhysicalVerificationListItem(BaseModel):
    dc_no: str
    vendor_name: str
    material_code: str
    verification_status: str
    physical_verification_status: str