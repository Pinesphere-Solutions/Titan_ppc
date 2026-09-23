"""In-memory mock SAP client for local development and testing — used
while the real SAP integration is unconfirmed/unreachable (architecture
doc Section 7.6). Lets M4–M13 be built and demoed end-to-end today.

Sample data below covers the SAP fields confirmed in the Titan SAP Data
Mapping Module design doc (Section 3): DC Number, Line Item Count,
Vendor Code/Name, Movement Type codes (101/313/321), and PO fields
(po_number/po_line_item/po_quantity) needed for Open PO / Pending
Quantity (Section 5, computed app-side per that doc's decision).

Notes:
- DC-1001 and DC-1003 deliberately share PO-5001 / line 10 — this
  exercises the "PO fulfilled across multiple partial deliveries"
  aggregation logic in app/integrations/sap/open_po.py.
- DC-1004 is left deliberately unverified (pending) on every fresh sync,
  for demonstrating DC Verification's "less" / deviation path against a
  vendor with NO email on file (the warning-log fallback path).
- DC-1005 is the same idea, but against VEND-02 — use this one once
  VEND-02 has an email set, to demonstrate the real notification path
  (the actual [mail:mock] send line, not the missing-email warning)."""

from typing import Any


class MockSAPClient:
    def __init__(self) -> None:
        self._posted_ud: dict[str, dict[str, Any]] = {}
        self._posted_313: dict[str, dict[str, Any]] = {}

    async def fetch_dispatched_materials(self) -> list[dict[str, Any]]:
        return [
            {
                "sap_document_no": "SAMPLE-0001",
                "dc_no": "DC-1001",
                "line_item_count": 3,
                "vendor_code": "VEND-01",
                "vendor_name": "Sri Balaji Polishing Works",
                "material_code": "MAT-CASE-FRONT-01",
                "model": "MODEL-A",
                "quantity_front_case": 250,
                "quantity_back_case": 250,
                "dispatch_date": "2026-09-01",
                "po_number": "PO-5001",
                "po_line_item": "10",
                "po_quantity": 1000,
            },
            {
                "sap_document_no": "SAMPLE-0002",
                "dc_no": "DC-1002",
                "line_item_count": 13,
                "vendor_code": "VEND-02",
                "vendor_name": "Coimbatore Precision Plating",
                "material_code": "MAT-CASE-BACK-02",
                "model": "MODEL-B",
                "quantity_front_case": 500,
                "quantity_back_case": 460,
                "dispatch_date": "2026-09-03",
                "po_number": "PO-5002",
                "po_line_item": "10",
                "po_quantity": 960,
            },
            {
                "sap_document_no": "SAMPLE-0003",
                "dc_no": "DC-1003",
                "line_item_count": 1,
                "vendor_code": "VEND-01",
                "vendor_name": "Sri Balaji Polishing Works",
                "material_code": "MAT-CASE-FRONT-02",
                "model": "MODEL-A",
                "quantity_front_case": 100,
                "quantity_back_case": 100,
                "dispatch_date": "2026-09-05",
                # Second partial delivery against the SAME PO line as DC-1001.
                "po_number": "PO-5001",
                "po_line_item": "10",
                "po_quantity": 1000,
            },
            {
                "sap_document_no": "SAMPLE-0004",
                "dc_no": "DC-1004",
                "line_item_count": 1,
                "vendor_code": "VEND-02",
                "vendor_name": "Coimbatore Precision Plating",
                "material_code": "MAT-CASE-BACK-03",
                "model": "MODEL-B",
                "quantity_front_case": 150,
                "quantity_back_case": 150,
                "dispatch_date": "2026-09-10",
                "po_number": "PO-5003",
                "po_line_item": "10",
                "po_quantity": 300,
            },
            {
                "sap_document_no": "SAMPLE-0005",
                "dc_no": "DC-1005",
                "line_item_count": 1,
                "vendor_code": "VEND-02",
                "vendor_name": "Coimbatore Precision Plating",
                "material_code": "MAT-CASE-BACK-04",
                "model": "MODEL-B",
                "quantity_front_case": 150,
                "quantity_back_case": 150,
                "dispatch_date": "2026-09-11",
                "po_number": "PO-5004",
                "po_line_item": "10",
                "po_quantity": 300,
            },
            {
                # Fresh, untouched test record — added to walk a brand new
                # DC through the full M4-M13 pipeline end-to-end for a demo,
                # since DC-1001/1002/1003 already completed it earlier.
                "sap_document_no": "SAMPLE-0006",
                "dc_no": "DC-1006",
                "line_item_count": 1,
                "vendor_code": "VEND-01",
                "vendor_name": "Sri Balaji Polishing Works",
                "material_code": "MAT-CASE-FRONT-03",
                "model": "MODEL-A",
                "quantity_front_case": 200,
                "quantity_back_case": 200,
                "dispatch_date": "2026-09-20",
                "po_number": "PO-5005",
                "po_line_item": "10",
                "po_quantity": 200,
            },
        ]

    async def fetch_movements(self) -> list[dict[str, Any]]:
        """Sample movement records covering the three confirmed movement
        types (101 Goods Receipt, 313 Stock Transfer, 321 Quality to
        Unrestricted). Posting date format is [OPEN] — treat this as
        illustrative only."""
        return [
            {
                "material_document_no": "MDOC-9001",
                "movement_type": "101",
                "dc_no": "DC-1001",
                "posting_date": "2026-09-06",
            },
            {
                "material_document_no": "MDOC-9002",
                "movement_type": "313",
                "dc_no": "DC-1001",
                "posting_date": "2026-09-07",
            },
            {
                "material_document_no": "MDOC-9003",
                "movement_type": "321",
                "dc_no": "DC-1002",
                "posting_date": "2026-09-08",
            },
        ]

    async def post_ud(self, dc_no: str, payload: dict[str, Any]) -> dict[str, Any]:
        # Idempotent: repeated calls with the same dc_no return the same result.
        if dc_no not in self._posted_ud:
            self._posted_ud[dc_no] = {"dc_no": dc_no, "status": "posted", **payload}
        return self._posted_ud[dc_no]

    async def post_313(self, dc_no: str, payload: dict[str, Any]) -> dict[str, Any]:
        if dc_no not in self._posted_313:
            self._posted_313[dc_no] = {"dc_no": dc_no, "status": "posted", **payload}
        return self._posted_313[dc_no]

    async def aclose(self) -> None:
        return None
