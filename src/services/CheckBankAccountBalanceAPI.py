from src.services.service import ServiceABC
from typing import Any, Dict

class CheckBankAccountBalanceAPI(ServiceABC):
    # url = self.baseurl + 'um/bank/account/balance'
    def getUrl(self) -> str:
        """Return the URL for the CheckBankAccountBalanceAPI request."""
        return self.baseurl + 'um/bank/account/balance'

    def getPayload(self, bankAcId: int, pin: str) -> Dict:
        """Create the JSON payload for the CheckBankAccountBalanceAPI request."""
        return {
            "bankAccId": bankAcId,
            "bankPin": pin
        }

    def parseResponse(self, response_data: Any) -> Any:
        """Parse the JSON response from the CheckBankAccountBalanceAPI request."""
        if response_data and isinstance(response_data, dict):
            if response_data.get("responseCode") == 200:
                return {
                    "status": True,
                    "balance": response_data.get("data", "0")
                }
            self.validation_error = f"Validation failed: {response_data.get('error', 'Invalid response')}"
        else:
            self.validation_error = "Validation failed: Invalid response"
        return None