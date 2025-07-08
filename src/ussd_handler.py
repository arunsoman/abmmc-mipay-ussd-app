import logging
from typing import Dict, Any
from src.gw.ussd_parser import USSDParser
from src.menu.graph.menu_state_management import MenuSessionManager
from src.gw.ussd_session_utils import USSDSessionManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("USSDHandler")

class USSDGatewayHandler:
    def __init__(self, config_mapping: Dict[str, Dict], session_timeout: int = 300000, max_pin_attempts: int = 3):
        self.parser = USSDParser(USSDSessionManager(session_timeout))
        self.menu_state_machine = MenuSessionManager(session_timeout_minutes=session_timeout // 60000)
        self.config_mapping = config_mapping  # Dictionary mapping dial strings to configs, e.g., {"*222#": config, "*222#1": config2}

    def handle_request(self, raw_xml: str) -> str:
        try:
            # Parse incoming XML
            parsed = self.parser.parse_request(raw_xml)
            logger.debug(f"Parsed request: {parsed}")
            dialog_type = parsed['dialog_type']
            msisdn = parsed['msisdn']
            user_input = parsed['user_input']

            if dialog_type == "Begin":
                service_code = user_input  # Initial dial string, e.g., "*222#" or "*222#1"
                if service_code not in self.config_mapping:
                    return self._generate_error_response("Service not configured yet")
                # Valid service code, use the corresponding config
                config = self.config_mapping[service_code]
                menu_engine = self.menu_state_machine.get_or_create_session(msisdn, config=config)
                response = menu_engine.get_current_prompt()  # Should be ValidationGateNode's prompt
                end_session = False
            else:  # Continue
                menu_engine = self.menu_state_machine.get_or_create_session(msisdn)
                response = menu_engine.process_user_input(user_input)
                end_session = True if user_input == "0" or response == "Session ended" else False
            response_xml = self.parser.getResponse(msisdn, response, end_session)
            logger.debug(f"Generated response: {response_xml}")
            return response_xml

        except Exception as e:
            logger.exception("Critical error handling request")
            return self._generate_error_response(str(e))

    def _generate_error_response(self, error_msg: str) -> str:
        error_xml = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <dialog type="End" mapMessagesSize="1">
            <processUnstructuredSSRequest_Response 
                dataCodingScheme="15" 
                string="{error_msg}"/>
        </dialog>
        """
        logger.error(f"Returning error response: {error_msg}")
        return error_xml
    



# Example usage
if __name__ == "__main__":
    from src.menu.graph.demo_menu_config import config
    config_mapping = {
    "*222#": config,  # Default config from demo_menu_config.py
    "*222#1": config  # Example: same config, but could be config2
    # Add more mappings as needed, e.g., "*222#1": config2
}

    handler = USSDGatewayHandler(config_mapping)
    
    # Sample begin request XML
    sample_begin ="""<?xml version="1.0" encoding="UTF-8"?> <dialog type="Begin" appCntx="networkUnstructuredSsContext_version2" networkId="0" 
    localId="SESSION123" remoteId="REMOTE123" mapMessagesSize="1" 
    returnMessageOnError="false">
        <localAddress pc="7725" ssn="147">
            <ai value="19"/>
            <gt type="GlobalTitle0100" tt="0" es="2" np="1" nai="4" digits="9370260024"/>
        </localAddress>
        <remoteAddress pc="0" ssn="6">
            <ai value="18"/>
            <gt type="GlobalTitle0100" tt="0" es="1" np="1" nai="4" digits="93702990008"/>
        </remoteAddress>
        <destinationReference number="412012115087574" nai="international_number" 
        npi="land_mobile"/>
        <originationReference number="93702990008" nai="international_number" npi="ISDN"/>
        <processUnstructuredSSRequest_Request invokeId="1" dataCodingScheme="15" 
        string="*222#">
            <msisdn number="93701234567" nai="international_number" npi="ISDN"/> 
        </processUnstructuredSSRequest_Request>
    </dialog>
    """
    
    # Process request
    response = handler.handle_request(sample_begin)
    print("Generated response:\n", response)

    print("\n\n Resp :", handler.handle_request(
    """<?xml version="1.0" encoding="UTF-8"?>
<dialog type="Continue" localId="SESSION123" remoteId="REMOTE123" appCntx="networkUnstructuredSsContext_version2" networkId="0" mapMessagesSize="1" returnMessageOnError="false">
    <unstructuredSSRequest_Response invokeId="1" dataCodingScheme="15" string="123456">
        <msisdn number="93701234567" nai="international_number" npi="ISDN"/>
    </unstructuredSSRequest_Response>
</dialog>
    """
        ))
# Example usage
