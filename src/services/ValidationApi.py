from src.services.service import ServiceABC
from typing import Any, Dict

class Validate(ServiceABC):
    def getUrl(self) -> str:
        return self.baseurl + "/aaa/USSDLogin"

    def getPayload(self) -> Dict:
        return {}

    def parseResponse(self, response_data: Any) -> Any:
        """Parse the JSON response from the BankTransactionAPI request."""
        try:
            return {
                    "auth_token": response_data.get("data")['auth_token'],
                }
        except Exception as e:
            print("something bad happed " +str(e))
            return None
        