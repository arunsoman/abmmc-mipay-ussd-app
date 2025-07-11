# url = self.baseurl + 'um/bank'
def getUrl(self) -> str:
    """Return the URL for the GetBanksListAPI request."""
    return self.baseurl + 'um/bank'

def getPayload(self) -> dict:
    """Create the JSON payload for the GetBanksListAPI request."""
    return {}  # GET request, no payload

def parseResponse(self, response_data: Any) -> Any:
    """Parse the JSON response from the GetBanksListAPI request."""
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