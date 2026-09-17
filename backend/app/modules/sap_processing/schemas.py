
from pydantic import BaseModel


class MovementItem(BaseModel):
    material_document_no: str
    movement_type: str
    dc_no: str
    posting_date: str | None = None
    sync_status: str