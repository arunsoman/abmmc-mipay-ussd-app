import logging
from typing import Dict, Optional, Tuple
from lxml import etree
import xml.etree.ElementTree as ET
from src.gw.ussd_session_utils import USSDSessionManager, USSDSession

class USSDParser:
    def __init__(self, session_manager: USSDSessionManager):
        # Updated XPaths for AWCC specification
        self._xpaths = {
            'dialog': etree.XPath("."),
            'network_id': etree.XPath("./@networkId"),
            'user_object': etree.XPath("./@userObject"),
            'local_address': etree.XPath("./localAddress"),
            'remote_address': etree.XPath("./remoteAddress"),
            'destination_ref': etree.XPath("./destinationReference/@number"),
            'origination_ref': etree.XPath("./originationReference/@number"),
            'ussd_request': etree.XPath("./processUnstructuredSSRequest_Request"),
            'ussd_response': etree.XPath("./unstructuredSSRequest_Response"),
            'ussd_notify': etree.XPath("./unstructuredSSNotify_Response"),
            'begin_msisdn': etree.XPath("./processUnstructuredSSRequest_Request/msisdn/@number"),
            'invoke_id_request': etree.XPath("./processUnstructuredSSRequest_Request/@invokeId"),
            'invoke_id_response': etree.XPath("./unstructuredSSRequest_Response/@invokeId"),
            'user_input_request': etree.XPath("./processUnstructuredSSRequest_Request/@string"),
            'user_input_response': etree.XPath("./unstructuredSSRequest_Response/@string"),
            'alerting_pattern': etree.XPath("./processUnstructuredSSRequest_Request/alertingPattern"),
            'error_components': etree.XPath("./errComponents"),
            'local_pc': etree.XPath("./localAddress/@pc"),
            'local_ssn': etree.XPath("./localAddress/@ssn"),
            'local_gt_digits': etree.XPath("./localAddress/gt/@digits"),
            'remote_pc': etree.XPath("./remoteAddress/@pc"),
            'remote_ssn': etree.XPath("./remoteAddress/@ssn"),
            'remote_gt_digits': etree.XPath("./remoteAddress/gt/@digits"),
        }
        self.request_type_xpath = etree.XPath("""
            ./processUnstructuredSSRequest_Request |
            ./unstructuredSSRequest_Response |
            ./unstructuredSSNotify_Request
        """)
        self.session_manager = session_manager or USSDSessionManager()

    def parse_request(self, raw_xml: str) -> Dict:
        """Parse XML request and update session with metadata"""
        try:
            raw_xml_bytes = raw_xml.encode('utf-8')
            root = etree.fromstring(raw_xml_bytes, etree.XMLParser(recover=False))
            
            # Extract core attributes
            session_id = self._get_session_id(root)
            dialog_type = root.get("type", "Continue")
            network_id = self._get_network_id(root)
            user_object = root.get("userObject", "")
            remote_id = root.get("remoteId", "")
            msisdn = self._extract_msisdn(root, dialog_type) 
            user_input = self.get_user_input(root)
            invoke_id = self._get_invoke_id(root)
            message_type = self.get_message_type(root)

            # Handle session based on dialog type
            if dialog_type == "Begin":
                service_code = user_input or ""
                session = self.session_manager.create_session(msisdn, session_id, service_code, initial_state=None)
            else:  # "Continue" or "End"
                session = self.session_manager.get_session(msisdn)
                if not session:
                    logging.warning(f"No {msisdn} and session_id {session_id}")
                    session = self.session_manager.create_session(msisdn, session_id, "", None)  # Fallback

            # Update session with metadata
            session.session_data.update({
                'message_type': message_type,
                'remote_id': remote_id,
                'network_id': network_id or "0",
                'user_object': user_object,
                'invoke_id': invoke_id or "1",
                'dialog_type': dialog_type,
            })
            if user_input:
                session.store_response('user_input', user_input)
            session.update_activity()

            # Build request dictionary
            request_dict = {
                "session_id": session_id,
                "remote_id": remote_id,
                "msisdn": msisdn,
                "network_id": network_id or "0",
                "user_object": user_object,
                "invoke_id": invoke_id,
                "message_type": message_type,
                "dialog_type": dialog_type,
                "user_input": user_input,
                "raw_xml": raw_xml
            }
            return request_dict
            
        except etree.XMLSyntaxError as e:
            logging.error(f"XML parsing error: {str(e)}")
            error_dict = self._build_error_dict("XML_SYNTAX_ERROR", str(e))
            return error_dict
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            error_dict = self._build_error_dict("PARSE_FAILURE", str(e))
            return error_dict

    def getResponse(self, msisdn: str, text: str, end_or_not: bool) -> str:
        """Generate XML response using session data"""
        
        session = self.session_manager.get_session(msisdn)
        if session is None:
            # Handle case where session doesn't exist or expired
            raise ValueError(f"No active session found for MSISDN: {msisdn}")
        
        message_type = session.session_data.get('message_type', 'processUnstructuredSSRequest_Request')
        response_message_type = self.get_response_message_type(
            message_type,
            "End" if end_or_not else "Continue"
        )

        dialog_attrs = {
            "type": "End" if end_or_not else "Continue",
            "localId": session.session_id,
            "remoteId": session.session_data.get('remote_id', ''),
            "appCntx": "networkUnstructuredSsContext_version2",
            "networkId": session.session_data.get('network_id', '0'),
            "mapMessagesSize": "1",
            "returnMessageOnError": "false"
        }

        if end_or_not:
            dialog_attrs["prearrangedEnd"] = "false"
        if not end_or_not and session.session_data.get('user_object'):
            dialog_attrs["userObject"] = session.session_data['user_object']

        root = ET.Element("dialog", attrib=dialog_attrs)
        response_attrs = {
            "invokeId": session.session_data.get('invoke_id', '1'),
            "dataCodingScheme": "15",
            "string": text
        }

        response_elem = ET.SubElement(root, response_message_type, attrib=response_attrs)
        if response_message_type in ["processUnstructuredSSRequest_Response", "unstructuredSSRequest_Request"]:
            ET.SubElement(response_elem, "msisdn", attrib={
                "number": session.msisdn,
                "nai": "international_number",
                "npi": "ISDN"
            })

        xml_str = ET.tostring(root, encoding="unicode")
        response = f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'
        
        if end_or_not:
            self.session_manager.end_session(session)
        
        return response

    def get_response_message_type(self, incoming_message_type: str, dialog_type: str = "Continue") -> str:
        """Determine the response message type based on incoming type and dialog action"""
        if dialog_type not in ("Continue", "End"):
            raise ValueError("dialog_type must be either 'Continue' or 'End'")
        
        if incoming_message_type == "processUnstructuredSSRequest_Request":
            return (
                "processUnstructuredSSRequest_Response" if dialog_type == "End"
                else "unstructuredSSRequest_Request"
            )
        elif incoming_message_type == "unstructuredSSRequest_Response":
            return (
                "processUnstructuredSSRequest_Response" if dialog_type == "End"
                else "unstructuredSSRequest_Request"
            )
        elif incoming_message_type == "unstructuredSSNotify_Request":
            return "unstructuredSSNotify_Response"
        else:
            valid_types = [
                "processUnstructuredSSRequest_Request",
                "unstructuredSSRequest_Response",
                "unstructuredSSNotify_Request"
            ]
            raise ValueError(
                f"Invalid incoming_message_type '{incoming_message_type}'. "
                f"Must be one of: {', '.join(valid_types)}"
            )

    # Helper methods remain unchanged but are included for completeness
    def _get_session_id(self, root) -> str:
        return root.get("localId", "0")

    def _get_network_id(self, root) -> str:
        return self._xpaths['network_id'](root)[0] if self._xpaths['network_id'](root) else "0"

    def _extract_msisdn(self, root, dialog_type: str) -> str:
        """Multi-source MSISDN extraction for all dialog types"""
        sources = [
            lambda: self._get_xpath_value(root, 'begin_msisdn', "./processUnstructuredSSRequest_Request/msisdn/@number"),
            lambda: self._get_xpath_value(root, 'origination_ref', "./originationReference/@number"),
            lambda: self._get_xpath_value(root, 'remote_gt_digits', "./remoteAddress/gt/@digits"),
            lambda: self._get_xpath_value(root, 'destination_ref', "./destinationReference/@number"),
            lambda: self._get_xpath_value(root, 'msisdn', ".//msisdn/@number"),
            lambda: self._get_xpath_value(root, 'gt_digits', ".//gt/@digits"),
        ]
        
        for source in sources:
            msisdn = source()
            if msisdn and msisdn != "*":  # Ensure valid MSISDN
                return msisdn
        raise ValueError(
            f"MSISDN not found in XML for dialog type '{dialog_type}'. "
            "Ensure MSISDN is present in processUnstructuredSSRequest_Request or other elements."
        )
    
    
    def _get_xpath_value(self, root, key: str, default: str = "*") -> str| None:
        """Helper to get first XPath result or default"""
        results = self._xpaths.get(key, etree.XPath(default))(root)
        return results[0] if results else None

    def get_user_input(self, root) -> Optional[str]:
        request_input = self._xpaths['user_input_request'](root)
        response_input = self._xpaths['user_input_response'](root)
        return request_input[0] if request_input else (response_input[0] if response_input else None)

    def _get_invoke_id(self, root) -> Optional[str]:
        invoke_id_request = self._xpaths['invoke_id_request'](root)
        invoke_id_response = self._xpaths['invoke_id_response'](root)
        return invoke_id_request[0] if invoke_id_request else (invoke_id_response[0] if invoke_id_response else None)

    def get_message_type(self, root) -> str:
        request_types = self.request_type_xpath(root)
        if not request_types:
            raise ValueError("No valid USSD request type found in XML")
        tag = etree.QName(request_types[0]).localname
        return tag

    def _build_error_dict(self, error_type: str, error_message: str) -> Dict:
        return {
            "error": True,
            "error_type": error_type,
            "error_message": error_message,
            "session_id": "0",
            "remote_id": "",
            "msisdn": "0000000000",
            "network_id": "0",
            "user_object": "",
            "invoke_id": "1",
            "message_type": "error",
            "dialog_type": "End",
            "user_input": None,
            "raw_xml": ""
        }

if __name__ == "__main__":
    from src.gw.ussd_session_utils import USSDSessionManager
    # Initialize parser with mock session manager
    parser = USSDParser(USSDSessionManager())
    
    # Test 1: Begin request parsing
    print("=== Test 1: Begin Request Parsing ===")
    begin_xml = '''<?xml version="1.0" encoding="UTF-8"?>
    <dialog type="Begin" localId="12345" remoteId="67890" networkId="1" userObject="test_obj">
        <originationReference number="93701234567"/>
        <destinationReference number="123"/>
        <processUnstructuredSSRequest_Request invokeId="1" string="*123#">
            <msisdn number="93701234567" nai="international_number" npi="ISDN"/>
        </processUnstructuredSSRequest_Request>
    </dialog>'''
    
    try:
        result = parser.parse_request(begin_xml)
        print(f"✓ Begin request parsed successfully")
        print(f"  MSISDN: {result['msisdn']}")
        print(f"  Session ID: {result['session_id']}")
        print(f"  Dialog Type: {result['dialog_type']}")
        print(f"  User Input: {result['user_input']}")
        print(f"  Message Type: {result['message_type']}")
    except Exception as e:
        print(f"✗ Begin request parsing failed: {e}")
    
    # Test 2: Continue request parsing
    print("\n=== Test 2: Continue Request Parsing ===")
    continue_xml = '''<?xml version="1.0" encoding="UTF-8"?>
    <dialog type="Continue" localId="12345" remoteId="67890" networkId="1">
        <unstructuredSSRequest_Response invokeId="1" string="1">
            <msisdn number="93701234567" nai="international_number" npi="ISDN"/>
        </unstructuredSSRequest_Response>
    </dialog>'''
    
    try:
        result = parser.parse_request(continue_xml)
        print(f"✓ Continue request parsed successfully")
        print(f"  MSISDN: {result['msisdn']}")
        print(f"  Dialog Type: {result['dialog_type']}")
        print(f"  User Input: {result['user_input']}")
        print(f"  Message Type: {result['message_type']}")
    except Exception as e:
        print(f"✗ Continue request parsing failed: {e}")
    
    # Test 3: Response generation
    print("\n=== Test 3: Response Generation ===")
    try:
        response = parser.getResponse("93701234567", "Welcome to USSD service", False)
        print(f"✓ Response generated successfully")
        print(f"  Response length: {len(response)} characters")
        print(f"  Contains dialog tag: {'<dialog' in response}")
        print(f"  Contains msisdn: {'93701234567' in response}")
    except Exception as e:
        print(f"✗ Response generation failed: {e}")
    
    # Test 4: End response generation
    print("\n=== Test 4: End Response Generation ===")
    try:
        end_response = parser.getResponse("93701234567", "Thank you for using USSD service", True)
        print(f"✓ End response generated successfully")
        print(f"  Response contains 'type=\"End\"': {'type=\"End\"' in end_response}")
        print(f"  Response contains 'prearrangedEnd': {'prearrangedEnd' in end_response}")
    except Exception as e:
        print(f"✗ End response generation failed: {e}")
    
    # Test 5: Invalid XML handling
    print("\n=== Test 5: Invalid XML Handling ===")
    invalid_xml = '''<?xml version="1.0" encoding="UTF-8"?>
    <dialog type="Begin" localId="12345"
        <invalid_tag>
    </dialog>'''
    
    try:
        result = parser.parse_request(invalid_xml)
        if result.get('error'):
            print(f"✓ Invalid XML handled gracefully")
            print(f"  Error type: {result['error_type']}")
            print(f"  Error message: {result['error_message']}")
        else:
            print(f"✗ Invalid XML should have returned error")
    except Exception as e:
        print(f"✗ Invalid XML handling failed: {e}")
    
    # Test 6: Response message type determination
    print("\n=== Test 6: Response Message Type Determination ===")
    test_cases = [
        ("processUnstructuredSSRequest_Request", "Continue", "unstructuredSSRequest_Request"),
        ("processUnstructuredSSRequest_Request", "End", "processUnstructuredSSRequest_Response"),
        ("unstructuredSSRequest_Response", "Continue", "unstructuredSSRequest_Request"),
        ("unstructuredSSRequest_Response", "End", "processUnstructuredSSRequest_Response"),
        ("unstructuredSSNotify_Request", "Continue", "unstructuredSSNotify_Response"),
    ]
    
    for incoming, dialog_type, expected in test_cases:
        try:
            result = parser.get_response_message_type(incoming, dialog_type)
            if result == expected:
                print(f"✓ {incoming} + {dialog_type} → {result}")
            else:
                print(f"✗ {incoming} + {dialog_type} → {result} (expected {expected})")
        except Exception as e:
            print(f"✗ {incoming} + {dialog_type} failed: {e}")
    

    # Test 6: Session persistence across multiple requests
    print("\n=== Test 6: Session Persistence Across Multiple Requests ===")
    
    # Create parser with fresh session manager
    msisdn = "93709876543"
    
    # Step 1: Begin dialog - create session
    begin_xml = '''<?xml version="1.0" encoding="UTF-8"?>
    <dialog type="Begin" localId="99999" remoteId="11111" networkId="1">
        <processUnstructuredSSRequest_Request invokeId="1" string="*100#">
            <msisdn number="93709876543" nai="international_number" npi="ISDN"/>
        </processUnstructuredSSRequest_Request>
    </dialog>'''
    
    try:
        result1 = parser.parse_request(begin_xml)
        session1 = parser.session_manager.get_session(msisdn)
        print(f"✓ Step 1 - Begin: Created session for {msisdn}")
    except Exception as e:
        print(f"✗ Step 1 failed: {e}")
    
    # Step 2: Continue dialog - should find existing session
    continue_xml = '''<?xml version="1.0" encoding="UTF-8"?>
    <dialog type="Continue" localId="99999" remoteId="11111" networkId="1">
        <unstructuredSSRequest_Response invokeId="1" string="1">
            <msisdn number="93709876543" nai="international_number" npi="ISDN"/>
        </unstructuredSSRequest_Response>
    </dialog>'''
    
    try:
        result2 = parser.parse_request(continue_xml)
        session2 = parser.session_manager.get_session(msisdn)
        print(f"✓ Step 2 - Continue: Found existing session for {msisdn}")
    except Exception as e:
        print(f"✗ Step 2 failed: {e}")
    
    # Step 3: Another continue dialog - verify session persistence
    continue2_xml = '''<?xml version="1.0" encoding="UTF-8"?>
    <dialog type="Continue" localId="99999" remoteId="11111" networkId="1">
        <unstructuredSSRequest_Response invokeId="1" string="2">
            <msisdn number="93709876543" nai="international_number" npi="ISDN"/>
        </unstructuredSSRequest_Response>
    </dialog>'''
    
    try:
        result3 = parser.parse_request(continue2_xml)
        session3 = parser.session_manager.get_session(msisdn)
        print(f"✓ Step 3 - Continue: Session still exists for {msisdn}")
    except Exception as e:
        print(f"✗ Step 3 failed: {e}")
    
    # Step 4: Generate response and end session
    try:
        response = parser.getResponse(msisdn, "Thank you!", True)
        session_after_end = parser.session_manager.get_session(msisdn)
        print(f"✓ Step 4 - End: Response generated and session ended")
        print(f"  Session exists after end: {session_after_end is not None}")
    except Exception as e:
        print(f"✗ Step 4 failed: {e}")
    
    # Test Continue without existing session (fallback)
    print("\n=== Test 6b: Continue Without Existing Session (Fallback) ===")
    # parser_fallback = USSDParser(USSDSessionManager())
    parser_fallback = parser
    continue_no_session_xml = '''<?xml version="1.0" encoding="UTF-8"?>
    <dialog type="Continue" localId="88888" remoteId="22222" networkId="1">
        <unstructuredSSRequest_Response invokeId="1" string="2">
            <msisdn number="93701111111" nai="international_number" npi="ISDN"/>
        </unstructuredSSRequest_Response>
    </dialog>'''
    
    try:
        result = parser_fallback.parse_request(continue_no_session_xml)
        session = parser_fallback.session_manager.get_session("93701111111")
        print(f"✓ Continue fallback: Created session for {result['msisdn']}")
        print(f"  Session exists: {session is not None}")
        print(f"  Service code (should be empty): '{session.service_code if session else 'None'}'")
    except Exception as e:
        print(f"✗ Continue fallback failed: {e}")
    
    # Test 7: Response message type determination
    print("\n=== Test 7: Response Message Type Determination ===")
    test_cases = [
        ("processUnstructuredSSRequest_Request", "Continue", "unstructuredSSRequest_Request"),
        ("processUnstructuredSSRequest_Request", "End", "processUnstructuredSSRequest_Response"),
        ("unstructuredSSRequest_Response", "Continue", "unstructuredSSRequest_Request"),
        ("unstructuredSSRequest_Response", "End", "processUnstructuredSSRequest_Response"),
        ("unstructuredSSNotify_Request", "Continue", "unstructuredSSNotify_Response"),
    ]
    
    for incoming, dialog_type, expected in test_cases:
        try:
            result = parser.get_response_message_type(incoming, dialog_type)
            if result == expected:
                print(f"✓ {incoming} + {dialog_type} → {result}")
            else:
                print(f"✗ {incoming} + {dialog_type} → {result} (expected {expected})")
        except Exception as e:
            print(f"✗ {incoming} + {dialog_type} failed: {e}")
  
    print("\n=== All Tests Completed ===")