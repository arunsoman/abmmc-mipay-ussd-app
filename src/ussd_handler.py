import logging
from typing import Dict
from src.gw.ussd_parser import USSDParser
from src.gw.ussd_session_utils import USSDSessionManager
from src.menu.graph.menu_state_management import MenuSessionManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class USSDGatewayHandler:
    def __init__(self, config_mapping: Dict[str, Dict]):
        self.parser = USSDParser(USSDSessionManager())
        self.menu_state_machine = MenuSessionManager(session_timeout_seconds=300)
        self.menu_state_machine.set_config_mapping(config_mapping)
        self.config_mapping = config_mapping
        self.msisdn_config_map = {}

    def handle_request(self, raw_xml: str):
        parsed_data = self.parser.parse_request(raw_xml)
        dialog_type = parsed_data['dialog_type']
        user_input = parsed_data['user_input']
        msisdn = parsed_data['msisdn']

        try:
            
            if dialog_type == "Begin" and self.msisdn_config_map.get(msisdn):
                del self.msisdn_config_map[msisdn]

            menu_engine = self.msisdn_config_map.get(msisdn)
            if not menu_engine:
                # For new sessions
                if dialog_type == "Begin":
                    service_code = user_input or '*220#'
                    self.parser.session_manager.get_session(msisdn).store_response('service_code', service_code)
                else:
                    session = self.parser.session_manager.get_session(msisdn)
                    service_code = session.session_data.get('service_code', '*220#') if session else '*220#'

                config = self.config_mapping.get(service_code, {})
                menu_engine = self.menu_state_machine.get_or_create_session(
                    msisdn=msisdn,
                    service_code=service_code,
                    config=config
                )
                self.msisdn_config_map[msisdn] = menu_engine

            # Process user input for non-Begin requests
            if dialog_type == "Continue" and user_input:
                response = menu_engine.process_user_input(user_input)
            else:
                response = menu_engine.get_current_prompt()

            end_session = dialog_type == 'End' or not menu_engine.session_active
            return self.parser.getResponse(msisdn, response, end_session)

        except Exception as e:
            logger.error(f"Critical error handling request: {e}")
            return self.parser.getResponse(msisdn, f"Error: {str(e)}", True)

    def _generate_error_response(self, error_msg: str) -> str:
        error_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
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
    from timeit import timeit
    import cProfile
    import pstats
    from pstats import SortKey

    from config.demo_menu_config import config

    config_mapping = {
        "*222#": config,   # Default config from demo_menu_config.py
        "*222#1": config   # Example: same config, but could be config2
        # Add more mappings as needed
    }

    def test():
        handler = USSDGatewayHandler(config_mapping)

        # Sample begin request XML
        sample_begin = """<?xml version="1.0" encoding="UTF-8"?>
<dialog type="Begin" appCntx="networkUnstructuredSsContext_version2" networkId="0" 
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

        # Sample continue request XML
        sample_continue = """<?xml version="1.0" encoding="UTF-8"?>
<dialog type="Continue" localId="SESSION123" remoteId="REMOTE123" appCntx="networkUnstructuredSsContext_version2" networkId="0" mapMessagesSize="1" returnMessageOnError="false">
    <unstructuredSSRequest_Response invokeId="1" dataCodingScheme="15" string="123456">
        <msisdn number="93701234567" nai="international_number" npi="ISDN"/>
    </unstructuredSSRequest_Response>
</dialog>
"""
        print("\n\nResp :", handler.handle_request(sample_continue))

    def benchmarking():
        # Run the function 50 times and measure total time
        total_time = timeit('test()', globals=globals(), number=50)
        print(f'Total time for 50 runs: {total_time:.6f} seconds')
        print(f'Average time per run: {total_time/50:.6f} seconds')

    # Profiling
    cProfile.run('benchmarking()', 'output.pstats')
    p = pstats.Stats('output.pstats')
    p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(10)
