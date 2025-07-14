from src.services.service import ServiceABC
from typing import Any, Dict
from .TokenManager import TokenManager

class Validate(ServiceABC):
        
    def setMsisdn(self, msisdn:str):
        self.msisdn = msisdn
    

    def getUrl(self) -> str:
        return self.baseurl + "/aaa/USSDLogin"

    def getPayload(self) -> Dict:
        return {}

    def parseResponse(self, response_data: Any) -> Any:
        """Parse the JSON response from the BankTransactionAPI request."""
        try:
            auth_token= response_data.get("data")['auth_token']
            TokenManager.store_token(self.msisdn, auth_token)            
            return {
                    "auth_token": auth_token,
                }
        except Exception as e:
            print("something bad happed " +str(e))
            return None
        