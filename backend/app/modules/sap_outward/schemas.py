
from pydantic import BaseModel


class DispatchListItem(BaseModel):
    sap_document_no: str
    dc_no: str | None = None
    vendor_name: str
    material_code: str
    model: str | None = None
    quantity_front_case: int | None = None
    quantity_back_case: int | None = None
    dispatch_date: str | None = None
    verification_status: str | None = None


class OpenPoItem(BaseModel):
    po_number: str
    po_line_item: str | None = None
    po_quantity: int
    received_qty: int
    pending_qty: int