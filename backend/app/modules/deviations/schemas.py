
from datetime import datetime

from pydantic import BaseModel


class DeviationItem(BaseModel):
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