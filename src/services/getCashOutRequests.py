from src.services.service import ServiceABC
from typing import Any, Dict

class getCashOutRequests(ServiceABC):
    # url = self.baseurl + 'ts/api/transaction-services/findWithdrawalReq'
    def getUrl(self) -> str:
        """Return the URL for the getCashOutRequests request."""
        return self.baseurl + 'ts/api/transaction-services/findWithdrawalReq'

    def getPayload(self) -> Dict:
        """Create the JSON payload for the getCashOutRequests request."""
        return {}  # GET request, no payload

    def parseResponse(self, response_data: Any) -> Any:
        """Parse the JSON response from the getCashOutRequests request."""
        if response_data and isinstance(response_data, dict):
            if response_data.get("responseCode") == 200:
                return {
                    "status": True,
                    "data": response_data.get("data", [])
                }
            self.validation_error = f"Validation failed: {response_data.get('error', 'Invalid response')}"
        else:
            self.validation_error = "Validation failed: Invalid response"
        return None