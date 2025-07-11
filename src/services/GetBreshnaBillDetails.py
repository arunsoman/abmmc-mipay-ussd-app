from src.services.service import ServiceABC
from typing import Any, Dict

class GetBreshnaBillDetails(ServiceABC):
    # url = self.baseurl + 'ts/api/transaction-services/fetchBill?accountNo={billNumber}'
    def getUrl(self, billNumber: str) -> str:
        """Return the URL for the GetBreshnaBillDetails request."""
        return self.baseurl + f'ts/api/transaction-services/fetchBill?accountNo={billNumber}'

    def getPayload(self) -> Dict:
        """Create the JSON payload for the GetBreshnaBillDetails request."""
        return {}  # GET request, parameters in URL

    def parseResponse(self, response_data: Any) -> Any:
        """Parse the JSON response from the GetBreshnaBillDetails request."""
        if response_data and isinstance(response_data, dict):
            if response_data.get("responseCode") == 200:
                return {
                    "status": True,
                    "data": response_data.get("data", {})
                }
            self.validation_error = f"Validation failed: {response_data.get('error', 'Invalid response')}"
        else:
            self.validation_error = "Validation failed: Invalid response"
        return None