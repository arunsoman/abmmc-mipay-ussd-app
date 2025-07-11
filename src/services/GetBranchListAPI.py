from src.services.service import ServiceABC
from typing import Any, Dict

class GetBranchListAPI(ServiceABC):
    # url = self.baseurl + 'um/branch'
    def getUrl(self) -> str:
        """Return the URL for the GetBranchListAPI request."""
        return self.baseurl + 'um/branch'

    def getPayload(self) -> Dict:
        """Create the JSON payload for the GetBranchListAPI request."""
        return {}  # GET request, no payload

    def parseResponse(self, response_data: Any) -> Any:
        """Parse the JSON response from the GetBranchListAPI request."""
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