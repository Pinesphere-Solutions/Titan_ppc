"""Pydantic request/response schemas for M13 Storage Management.
Kept separate from ORM models — see architecture doc Section 5.2."""

from datetime import datetime

from pydantic import BaseModel


class StoragePendingItem(BaseModel):
    dc_no: str
    vendor_name: str
    material_code: str
    model: str | None
    quantity: int


class StorageAssignRequest(BaseModel):
    rack: str
    row: str
    bin: str
    storage_location: str


class StorageResponse(BaseModel):
    dc_no: str
    vendor_name: str
    rack: str
    row: str
    bin: str
    storage_location: str
    stored_by: str
    message: str


class StoredItem(BaseModel):
    dc_no: str
    vendor_name: str
    material_code: str
    model: str | None
    rack: str
    row: str
    bin: str
    storage_location: str
    stored_by: str
    stored_at: datetime
