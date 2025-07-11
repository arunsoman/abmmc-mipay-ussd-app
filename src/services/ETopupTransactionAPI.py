# url = self.baseurl + 'tms/api/tms/router/basic'
def getUrl(self) -> str:
    """Return the URL for the ETopupTransactionAPI request."""
    return self.baseurl + 'tms/api/tms/router/basic'

def getPayload(self, initiator: int, serviceProvider: int, serviceReceiver: int, serviceName: str, channel: str, amount: str, mobileNumber: str, pin: str) -> dict:
    """Create the JSON payload for the ETopupTransactionAPI request."""
    initiator_arr = {"id": initiator}
    service_provider_arr = {"id": serviceProvider}
    service_receiver_arr = {"id": serviceReceiver}
    context = {
        "SERVICE_NAME": serviceName,
        "MEDIUM": "IOS",
        "CHANNEL": channel,
        "AMOUNT": amount,
        "PIN": pin,
        "mobileNumber": mobileNumber
    }
    return {
        "initiator": initiator_arr,
        "serviceProvider": service_provider_arr,
        "serviceReceiver": service_receiver_arr,
        "context": context
    }

def parseResponse(self, response_data: Any) -> Any:
    """Parse the JSON response from the ETopupTransactionAPI request."""
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