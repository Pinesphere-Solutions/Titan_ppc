"""Pydantic request/response schemas for M11 QA Inspection.
Kept separate from ORM models — see architecture doc Section 5.2."""

from pydantic import BaseModel


class QaInspectionQueueItem(BaseModel):
    dc_no: str
    vendor_name: str
    material_code: str
    model: str
    inspection_status: str
    qa_user: str | None


class QaInspectionResponse(BaseModel):
    dc_no: str
    vendor_name: str
    inspection_status: str
    qa_user: str
    message: str
