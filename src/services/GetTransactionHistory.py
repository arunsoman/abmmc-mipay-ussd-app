from src.services.service import ServiceABC
from typing import Any, Dict

class GetTransactionHistory(ServiceABC):
    # url = self.baseurl + 'ts/api/transaction-services/getFilteredHistory?walletNo={walletNumber}&trxnType={type}&fromDate={from}&toDate={to}'
    def getUrl(self, walletNumber: str, type: str, from_date: str, to_date: str) -> str:
        """Return the URL for the GetTransactionHistory request."""
        return self.baseurl + f'ts/api/transaction-services/getFilteredHistory?walletNo={walletNumber}&trxnType={type}&fromDate={from_date}&toDate={to_date}'

    def getPayload(self) -> Dict:
        """Create the JSON payload for the GetTransactionHistory request."""
        return {}  # GET request, parameters in URL

    def parseResponse(self, response_data: Any) -> Any:
        """Parse the JSON response from the GetTransactionHistory request."""
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