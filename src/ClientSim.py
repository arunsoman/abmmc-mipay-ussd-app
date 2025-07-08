import requests
import xml.etree.ElementTree as ET
from xml.dom import minidom
import random
import uuid

class AWCCUSSDGatewayClient:
    """AWCC USSD Gateway Protocol Client - Acts as USSD Gateway Proxy"""
    
    def __init__(self, server_url: str, msisdn: str = "93701234567", ussd_code: str = "*224#"):
        self.server_url = server_url
        self.msisdn = msisdn
        self.ussd_code = ussd_code.rstrip('#')  # Remove trailing #
        self.remote_id = None  # Application's session ID
        self.user_object = None  # Session continuation object
        self.dialog_type = "Begin"
        self.invoke_id = 1
        
        # Generate unique session ID for this gateway session
        self.local_id = str(random.randint(10000000, 99999999))
        
        # AWCC Gateway addressing information
        self.local_pc = "7725"  # Point Code
        self.local_ssn = "147"  # Subsystem Number
        self.remote_ssn = "6"   # Application SSN
        self.gateway_gt = "9370260024"  # Gateway Global Title
        self.app_gt = "93702990008"     # Application Global Title
        
        # Generate destination reference (used for billing/routing)
        self.destination_ref = f"412012{random.randint(100000000, 999999999)}"
    
    def _create_request_xml(self, user_input: str = "") -> str:
        """Generate XML request based on session state"""
        if self.dialog_type == "Begin":
            return self._initial_request()
        elif self.dialog_type == "Continue":
            return self._continue_request(user_input)
        else:  # End
            return self._end_request(user_input)
    
    def _initial_request(self) -> str:
        """Create initial USSD request XML - Gateway to Application"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<dialog type="Begin" appCntx="networkUnstructuredSsContext_version2" networkId="0" 
        localId="{self.local_id}" remoteId="REMOTE_ID" mapMessagesSize="1" 
        returnMessageOnError="false">
    <localAddress pc="{self.local_pc}" ssn="{self.local_ssn}">
        <ai value="19"/>
        <gt type="GlobalTitle0100" tt="0" es="2" np="1" nai="4" digits="{self.gateway_gt}"/>
    </localAddress>
    <remoteAddress pc="0" ssn="{self.remote_ssn}">
        <ai value="18"/>
        <gt type="GlobalTitle0100" tt="0" es="1" np="1" nai="4" digits="{self.app_gt}"/>
    </remoteAddress>
    <destinationReference number="{self.destination_ref}" nai="international_number" npi="land_mobile"/>
    <originationReference number="{self.msisdn}" nai="international_number" npi="ISDN"/>
    <processUnstructuredSSRequest_Request invokeId="{self.invoke_id}" dataCodingScheme="15" 
            string="{self.ussd_code}#">
        <msisdn number="{self.msisdn}" nai="international_number" npi="ISDN"/>
    </processUnstructuredSSRequest_Request>
</dialog>"""
    
    def _continue_request(self, user_input: str) -> str:
        """Create continuation request XML - Gateway forwarding user response"""
        if not user_input.strip():
            user_input = ""  # Handle empty input gracefully
            
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<dialog type="Continue" appCntx="networkUnstructuredSsContext_version2" networkId="0" 
        localId="{self.local_id}" remoteId="{self.remote_id}" mapMessagesSize="1" 
        returnMessageOnError="false\""""
        
        if self.user_object:
            xml_content += f' userObject="{self.user_object}"'
        
        xml_content += f""">
    <localAddress pc="{self.local_pc}" ssn="{self.local_ssn}">
        <ai value="19"/>
        <gt type="GlobalTitle0100" tt="0" es="2" np="1" nai="4" digits="{self.gateway_gt}"/>
    </localAddress>
    <remoteAddress pc="0" ssn="{self.remote_ssn}">
        <ai value="18"/>
        <gt type="GlobalTitle0100" tt="0" es="1" np="1" nai="4" digits="{self.app_gt}"/>
    </remoteAddress>
    <destinationReference number="{self.destination_ref}" nai="international_number" npi="land_mobile"/>
    <originationReference number="{self.msisdn}" nai="international_number" npi="ISDN"/>
    <unstructuredSSRequest_Response invokeId="{self.invoke_id}" dataCodingScheme="15" 
            string="{user_input}"/>
</dialog>"""
        
        return xml_content
    
    def _end_request(self, user_input: str = "") -> str:
        """Create end dialog request XML"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<dialog type="End" mapMessagesSize="1" prearrangedEnd="false">
    <processUnstructuredSSRequest_Response invokeId="{self.invoke_id}" dataCodingScheme="15" 
            string="{user_input}"/>
</dialog>"""
    
    def _parse_response(self, xml_response: str) -> dict:
        """Extract information from server response"""
        try:
            root = ET.fromstring(xml_response)
        except ET.ParseError as e:
            return {
                "error": f"Invalid XML response: {str(e)}",
                "raw_response": xml_response
            }
        
        # Get server's session ID for our next request
        server_local_id = root.get('localId')
        if server_local_id and server_local_id != self.remote_id:
            self.remote_id = server_local_id
        
        # Get userObject for session continuity
        user_object = root.get('userObject')
        if user_object:
            self.user_object = user_object
        
        # Get dialog type from response
        response_dialog_type = root.get('type', 'Continue')
        
        # Extract message content - try multiple possible message elements
        message = "No message found"
        
        # Check for different message types based on dialog state
        message_elements = [
            './/unstructuredSSRequest_Request',  # Application requesting user input
            './/processUnstructuredSSRequest_Response',  # Final response
            './/unstructuredSSRequest_Response'  # User response (shouldn't be in app response)
        ]
        
        for element_path in message_elements:
            element = root.find(element_path)
            if element is not None:
                string_attr = element.get('string')
                if string_attr:
                    message = string_attr
                    break
        
        # Also check for ussd-string or string elements
        if message == "No message found":
            for xpath in ['.//ussd-string', './/string']:
                element = root.find(xpath)
                if element is not None and element.text:
                    message = element.text
                    break
        
        # Determine if this is the end of the session
        is_end = (response_dialog_type == "End" or 
                 root.find('.//processUnstructuredSSRequest_Response') is not None)
        
        return {
            "session_id": self.local_id,
            "remote_id": self.remote_id,
            "user_object": self.user_object,
            "dialog_type": response_dialog_type,
            "message": message,
            "is_end": is_end,
            "raw_xml": self._pretty_print_xml(xml_response),
            "msisdn": self.msisdn,
            "destination_ref": self.destination_ref
        }
    
    def _pretty_print_xml(self, xml_str: str) -> str:
        """Format XML for better readability"""
        if not xml_str.strip():
            return xml_str
        try:
            parsed = minidom.parseString(xml_str)
            return parsed.toprettyxml(indent="  ")
        except:
            return xml_str
    
    def send_request(self, user_input: str = "") -> dict:
        """Send USSD request to server and return response"""
        # Create XML request
        xml_request = self._create_request_xml(user_input)
        
        # Send to server
        try:
            response = requests.post(
                self.server_url,
                data=xml_request,
                headers={'Content-Type': 'application/xml'},
                timeout=15000
            )
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Connection failed: {str(e)}",
                "request_xml": self._pretty_print_xml(xml_request)
            }
        
        # Handle response
        if response.status_code != 200:
            return {
                "error": f"Server error: {response.status_code}",
                "response_text": response.text,
                "request_xml": self._pretty_print_xml(xml_request)
            }
        
        # Parse response and update state
        result = self._parse_response(response.text)
        if "error" not in result:
            # Update dialog type for next request
            if result.get('is_end'):
                self.dialog_type = "End"
            else:
                self.dialog_type = "Continue"
            
            # Increment invoke ID for next request
            self.invoke_id += 1
            
        return result
    
    def interactive_session(self):
        """Run interactive USSD simulation with AWCC Gateway Protocol"""
        print(f"\n{' Starting AWCC USSD Gateway Session ':=^80}")
        print(f"MSISDN: {self.msisdn}")
        print(f"USSD Code: {self.ussd_code}#")
        print(f"Gateway Session ID: {self.local_id}")
        print(f"Gateway GT: {self.gateway_gt}")
        print(f"Application GT: {self.app_gt}")
        print(f"Destination Reference: {self.destination_ref}\n")
        
        # Send initial request
        print("Sending initial USSD request...")
        response = self.send_request()
        
        if "error" in response:
            print(f"\nError: {response['error']}")
            if "request_xml" in response:
                print("\nRequest XML:")
                print(response["request_xml"])
            if "raw_response" in response:
                print("\nResponse XML:")
                print(response["raw_response"])
            return
        
        while True:
            # Print server response
            print("\n" + "="*80)
            print("Application Response:")
            print(response["message"])
            print(f"\nGateway Session ID: {response['session_id']}")
            print(f"Application Remote ID: {response['remote_id']}")
            print(f"User Object: {response['user_object']}")
            print(f"Dialog Type: {response['dialog_type']}")
            print(f"MSISDN: {response['msisdn']}")
            print(f"Destination Ref: {response['destination_ref']}")
            
            # Check if session ended
            if response.get('is_end'):
                print("\n" + "="*80)
                print("Session ended by application")
                print("="*80)
                break
                
            # Get user input
            print("\n" + "-"*60)
            user_input = input("Subscriber input (or 'exit' to quit, 'end' to end session): ").strip()
            
            if user_input.lower() == 'exit':
                print("Exiting session...")
                break
            
            if user_input.lower() == 'end':
                print("Ending session...")
                self.dialog_type = "End"
                response = self.send_request("Session ended by user")
                if "error" not in response:
                    print(f"\nFinal Response: {response['message']}")
                break
                
            # Send next request
            print(f"Forwarding user input: '{user_input}'")
            response = self.send_request(user_input)
            
            # Handle errors
            if "error" in response:
                print(f"\nError: {response['error']}")
                if "request_xml" in response:
                    print("\nRequest XML:")
                    print(response["request_xml"])
                if "raw_xml" in response:
                    print("\nResponse XML:")
                    print(response["raw_xml"])
                break
    
    def get_session_info(self) -> dict:
        """Get current session information"""
        return {
            "gateway_session_id": self.local_id,
            "app_remote_id": self.remote_id,
            "user_object": self.user_object,
            "dialog_type": self.dialog_type,
            "invoke_id": self.invoke_id,
            "msisdn": self.msisdn,
            "destination_ref": self.destination_ref,
            "gateway_gt": self.gateway_gt,
            "app_gt": self.app_gt
        }


if __name__ == "__main__":
    # Configuration - update with your application server details
    SERVER_URL = "http://localhost:3214/ussd"  # Your USSD application endpoint
    # SERVER_URL = "http://52.77.78.250:3214/ussd"
    TEST_MSISDN = "93701234567"  # Test subscriber number
    USSD_CODE = "*220"  # USSD code to test
    
    print("AWCC USSD Gateway Protocol Client")
    print("=================================")
    print("This client simulates the AWCC USSD Gateway sending requests to your application")
    print(f"Server URL: {SERVER_URL}")
    print(f"Test MSISDN: {TEST_MSISDN}")
    print(f"USSD Code: {USSD_CODE}#")
    
    # Start interactive session
    gateway_client = AWCCUSSDGatewayClient(SERVER_URL, TEST_MSISDN, USSD_CODE)
    
    try:
        gateway_client.interactive_session()
    except KeyboardInterrupt:
        print("\n\nSession interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    
    # Print final session info
    print("\nFinal Session Information:")
    session_info = gateway_client.get_session_info()
    for key, value in session_info.items():
        print(f"  {key}: {value}")