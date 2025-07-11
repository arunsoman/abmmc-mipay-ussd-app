from src.services.service import ServiceABC
from typing import Any, Dict

class GetBundleListAPI(ServiceABC):
    # url = self.baseurl + 'tms/serviceDetail/awcc/bundlePacks'
    def getUrl(self) -> str:
        """Return the URL for the GetBundleListAPI request."""
        return self.baseurl + 'tms/serviceDetail/awcc/bundlePacks'

    def getPayload(self) -> Dict:
        """Create the JSON payload for the GetBundleListAPI request."""
        return {}  # GET request, no payload

    def parseResponse(self, response_data: Any) -> Any:
        """Parse the JSON response from the GetBundleListAPI request."""
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