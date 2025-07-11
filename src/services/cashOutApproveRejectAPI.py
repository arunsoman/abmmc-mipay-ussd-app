# url = self.baseurl + 'ts/api/transaction-services/authorizeByApp?cashOutId={id}&value={status}&pin={pin}'
def getUrl(self, id: int, status: str, pin: str) -> str:
    """Return the URL for the cashOutApproveRejectAPI request."""
    return self.baseurl + f'ts/api/transaction-services/authorizeByApp?cashOutId={id}&value={status}&pin={pin}'

def getPayload(self) -> dict:
    """Create the JSON payload for the cashOutApproveRejectAPI request."""
    return {}  # GET request, parameters in URL

def parseResponse(self, response_data: Any) -> Any:
    """Parse the JSON response from the cashOutApproveRejectAPI request."""
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