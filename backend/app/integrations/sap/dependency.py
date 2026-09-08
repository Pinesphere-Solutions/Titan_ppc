"""FastAPI dependency that hands services a SAPClientInterface — real or
mock depending on config. This is the single switch point: flip
USE_MOCK_SAP_CLIENT in the environment once real SAP access is confirmed.
See architecture doc Section 5.2."""

from app.core.config import settings
from app.integrations.sap.interface import SAPClientInterface
from app.integrations.sap.mock_client import MockSAPClient

_sap_client: SAPClientInterface | None = None


def get_sap_client() -> SAPClientInterface:
    global _sap_client
    if _sap_client is None:
        if settings.use_mock_sap_client:
            _sap_client = MockSAPClient()  # type: ignore[assignment]
        else:
            from app.integrations.sap.client import SAPRestClient

            _sap_client = SAPRestClient()
    return _sap_client
