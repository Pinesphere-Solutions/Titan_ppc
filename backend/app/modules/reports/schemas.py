

from pydantic import BaseModel


class MovementHistoryEvent(BaseModel):
    dc_no: str
    vendor_name: str
    material_code: str
    event_type: str  # "received" | "qc_acknowledged" | "sap_movement"
    description: str
    quantity: int | None = None
    event_date: str