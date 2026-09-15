
from pydantic import BaseModel


class DcVerificationRequest(BaseModel):
    actual_front_case: int
    actual_back_case: int


class DcVerificationResponse(BaseModel):
    dc_no: str
    expected_qty: int
    actual_qty: int
    result: str  # "matched" | "excess" | "less"
    verification_status: str
    deviation_created: bool
    deviation_id: str | None = None