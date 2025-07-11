# url = self.baseurl + 'tms/api/tms/router/basic'
def getUrl(self) -> str:
    """Return the URL for the BundleTopupAPI request."""
    return self.baseurl + 'tms/api/tms/router/basic'

def getPayload(self, amount: str, service: str, mobileNo: str, code: str, pin: str) -> dict:
    """Create the JSON payload for the BundleTopupAPI request."""
    initiator_arr = {"id": getattr(self, 'user_id', 0)}  # Assuming user_id from UserProfileData
    service_provider_arr = {"id": getattr(self, 'user_id', 0)}
    service_receiver_arr = {"id": getattr(self, 'user_id', 0)}
    context = {
        "MEDIUM": "IOS",
        "AMOUNT": amount,
        "SERVICE_NAME": service,
        "mobileNumber": mobileNo,
        "bundle": code,
        "CHANNEL": "iOS",
        "PIN": pin
    }
    return {
        "initiator": initiator_arr,
        "serviceProvider": service_provider_arr,
        "serviceReceiver": service_receiver_arr,
        "context": context
    }

def parseResponse(self, response_data: Any) -> Any:
    """Parse the JSON response from the BundleTopupAPI request."""
    if response_data and isinstance(response_data, dict):
        if response_data.get("responseCode") == 200:
            status_code = response_data.get("data", {}).get("status_code", 0)
            return {
                "status": status_code == 200,
                "data": response_data.get("data", {})
            }
        self.validation_error = f"Validation failed: {response_data.get('error', 'Invalid response')}"
    else:
        self.validation_error = "Validation failed: Invalid response"
    return None