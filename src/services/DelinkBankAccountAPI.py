# url = self.baseurl + 'um/bank/account/remove'
def getUrl(self) -> str:
    """Return the URL for the DelinkBankAccountAPI request."""
    return self.baseurl + 'um/bank/account/remove'

def getPayload(self, acId: int, otp: str) -> dict:
    """Create the JSON payload for the DelinkBankAccountAPI request."""
    return {
        "bankAccId": acId,
        "otp": otp
    }

def parseResponse(self, response_data: Any) -> Any:
    """Parse the JSON response from the DelinkBankAccountAPI request."""
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