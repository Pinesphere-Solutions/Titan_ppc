

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


    
    @abstractmethod
    async def fetch_movements(self) -> list[dict[str, Any]]:
        """Pull movement records (101/313/321) for M9/M11/M12.
        Field shape TBC — see open item in Section 3 of the SAP mapping doc."""