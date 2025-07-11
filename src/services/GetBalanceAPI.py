# url = self.baseurl + 'ts/api/transaction-services/CurrentBalance'
def getUrl(self) -> str:
    """Return the URL for the GetBalanceAPI request."""
    return self.baseurl + 'ts/api/transaction-services/CurrentBalance'

def getPayload(self) -> dict:
    """Create the JSON payload for the GetBalanceAPI request."""
    return {}  # GET request, no payload

def parseResponse(self, response_data: Any) -> Any:
    """Parse the JSON response from the GetBalanceAPI request."""
    if response_data and isinstance(response_data, dict):
        if response_data.get("responseCode") == 200:
            return {
                "status": True,
                "balance": response_data.get("data", 0.0)
            }
        self.validation_error = f"Validation failed: {response_data.get('error', 'Invalid response')}"
    else:
        self.validation_error = "Validation failed: Invalid response"
    return None