
from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_dispatches: int
    pending_verification: int
    pending_qc_acknowledgement: int
    open_deviations: int
    total_movements_synced: int
    open_po_count: int
    total_pending_qty: int