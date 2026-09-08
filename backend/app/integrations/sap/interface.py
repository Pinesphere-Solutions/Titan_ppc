"""Abstract SAP client interface. Domain services depend on THIS, never on
the concrete REST client — see architecture doc Section 5.2 and Section 13
item 1 (SAP field-level scope is still pending confirmation). This is what
lets the rest of the system be built and tested today against the mock
client, with no refactor needed once the real SAP endpoints are confirmed.
"""

from abc import ABC, abstractmethod
from typing import Any


class SAPClientInterface(ABC):
    @abstractmethod
    async def fetch_dispatched_materials(self) -> list[dict[str, Any]]:
        """Pull dispatched material data (Titan -> Vendor) for M3.
        Field shape TBC — see open item in Section 13."""

    @abstractmethod
    async def post_ud(self, dc_no: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Submit a UD Post for the given delivery challan. Must be
        idempotent — see architecture doc Section 5.2."""

    @abstractmethod
    async def post_313(self, dc_no: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Submit a SAP 313 posting for the given delivery challan. Must be
        idempotent — see architecture doc Section 5.2."""
