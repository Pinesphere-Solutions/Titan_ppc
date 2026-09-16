from pydantic import BaseModel


class QcAcknowledgeResponse(BaseModel):
    dc_no: str
    qc_ack_status: str
    qc_acknowledged_by: str | None
    stock_level: str
    ud_post_status: str