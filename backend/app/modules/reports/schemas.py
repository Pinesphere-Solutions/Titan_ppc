
from datetime import datetime

from pydantic import BaseModel


class MovementHistoryEvent(BaseModel):
    dc_no: str
    vendor_name: str
    material_code: str
    event_type: str  # "received" | "qc_acknowledged" | "sap_movement"
    description: str
    quantity: int | None = None
    event_date: str


class VendorReportItem(BaseModel):
    vendor_code: str
    vendor_name: str
    total_dispatches: int
    total_dcs: int
    pending_qc: int
    total_deviations: int


class QcReportItem(BaseModel):
    dc_no: str
    vendor_name: str
    material_code: str
    qc_ack_status: str
    qc_acknowledged_by: str | None
    qc_acknowledged_at: datetime | None
    stock_level: str


class SapReportItem(BaseModel):
    dc_no: str
    vendor_name: str
    material_code: str
    material_document_no: str
    movement_type: str
    movement_label: str
    posting_date: str | None
    sync_status: str


class DeviationReportItem(BaseModel):
    dc_no: str
    vendor_name: str
    material_code: str
    deviation_type: str
    expected_qty: int
    actual_qty: int
    difference_qty: int
    mail_status: str
    vendor_status: str
    created_at: datetime


class StorageReportItem(BaseModel):
    dc_no: str
    vendor_name: str
    material_code: str
    rack: str
    row: str
    bin: str
    storage_location: str
    stored_by: str
    stored_at: datetime
