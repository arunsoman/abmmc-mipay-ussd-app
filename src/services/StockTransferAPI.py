from src.services.service import ServiceABC
from typing import Any, Dict

class StockTransferAPI(ServiceABC):
    # url = self.baseurl + 'tms/api/tms/router/basic'
    def getUrl(self) -> str:
        """Return the URL for the StockTransferAPI request."""
        return self.baseurl + 'tms/api/tms/router/basic'

    def getPayload(self, initiator: int, serviceProvider: int, serviceReceiver: int, serviceName: str, channel: str, amount: str, pin: str) -> Dict:
        """Create the JSON payload for the StockTransferAPI request."""
        initiator_arr = {"id": initiator}
        service_provider_arr = {"id": serviceProvider}
        service_receiver_arr = {"id": serviceReceiver}
        context = {
            "SERVICE_NAME": serviceName,
            "MEDIUM": "IOS",
            "CHANNEL": channel,
            "AMOUNT": amount,
            "PIN": pin
        }
        return {
            "initiator": initiator_arr,
            "serviceProvider": service_provider_arr,
            "serviceReceiver": service_receiver_arr,
            "context": context
        }

    def parseResponse(self, response_data: Any) -> Any:
        """Parse the JSON response from the StockTransferAPI request."""
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