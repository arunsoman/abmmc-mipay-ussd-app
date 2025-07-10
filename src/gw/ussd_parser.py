import logging
from typing import Dict, Optional, Tuple, List
from lxml import etree
import xml.etree.ElementTree as ET
from functools import lru_cache
from src.gw.ussd_session_utils import USSDSessionManager, USSDSession

class USSDParser:
    """Optimized USSD Parser with caching and performance improvements"""
    
    # Class-level constants to avoid repeated string creation
    DIALOG_TYPES = {"Begin", "Continue", "End"}
    MESSAGE_TYPES = {
        "processUnstructuredSSRequest_Request",
        "unstructuredSSRequest_Response", 
        "unstructuredSSNotify_Request"
    }
    
    # Pre-compiled response message type mappings
    RESPONSE_TYPE_MAP = {
        ("processUnstructuredSSRequest_Request", "Continue"): "unstructuredSSRequest_Request",
        ("processUnstructuredSSRequest_Request", "End"): "processUnstructuredSSRequest_Response",
        ("unstructuredSSRequest_Response", "Continue"): "unstructuredSSRequest_Request",
        ("unstructuredSSRequest_Response", "End"): "processUnstructuredSSRequest_Response",
        ("unstructuredSSNotify_Request", "Continue"): "unstructuredSSNotify_Response",
        ("unstructuredSSNotify_Request", "End"): "unstructuredSSNotify_Response",
    }
    
    # Pre-compiled XPath expressions as class attributes
    _XPATH_NETWORK_ID = etree.XPath("./@networkId")
    _XPATH_BEGIN_MSISDN = etree.XPath("./processUnstructuredSSRequest_Request/msisdn/@number")
    _XPATH_ORIGINATION_REF = etree.XPath("./originationReference/@number")
    _XPATH_REMOTE_GT_DIGITS = etree.XPath("./remoteAddress/gt/@digits")
    _XPATH_DESTINATION_REF = etree.XPath("./destinationReference/@number")
    _XPATH_MSISDN_ALL = etree.XPath(".//msisdn/@number")
    _XPATH_GT_DIGITS_ALL = etree.XPath(".//gt/@digits")
    _XPATH_USER_INPUT_REQUEST = etree.XPath("./processUnstructuredSSRequest_Request/@string")
    _XPATH_USER_INPUT_RESPONSE = etree.XPath("./unstructuredSSRequest_Response/@string")
    _XPATH_INVOKE_ID_REQUEST = etree.XPath("./processUnstructuredSSRequest_Request/@invokeId")
    _XPATH_INVOKE_ID_RESPONSE = etree.XPath("./unstructuredSSRequest_Response/@invokeId")
    _XPATH_REQUEST_TYPES = etree.XPath("""
        ./processUnstructuredSSRequest_Request |
        ./unstructuredSSRequest_Response |
        ./unstructuredSSNotify_Request
    """)
    
    def __init__(self, session_manager: USSDSessionManager):
        self.session_manager = session_manager or USSDSessionManager()
        
        # Pre-create XML parser for reuse
        self._xml_parser = etree.XMLParser(
            recover=False,
            strip_cdata=False,
            resolve_entities=False,  # Security: disable entity resolution
            huge_tree=False,
            collect_ids=False
        )
        
        # Cache for MSISDN extraction methods
        self._msisdn_extractors = [
            self._extract_begin_msisdn,
            self._extract_origination_ref,
            self._extract_remote_gt_digits,
            self._extract_destination_ref,
            self._extract_msisdn_all,
            self._extract_gt_digits_all,
        ]

    def parse_request(self, raw_xml: str) -> Dict:
        """Parse XML request with optimized error handling and caching"""
        try:
            # Fast path: reuse parser instance
            root = etree.fromstring(raw_xml.encode('utf-8'), self._xml_parser)
            
            # Extract attributes with minimal XPath calls
            dialog_type = root.get("type", "Continue")
            session_id = root.get("localId", "0")
            network_id = self._get_network_id_fast(root)
            user_object = root.get("userObject", "")
            remote_id = root.get("remoteId", "")
            
            # Extract MSISDN using optimized method
            msisdn = self._extract_msisdn_fast(root, dialog_type)
            
            # Extract user input and invoke ID
            user_input = self._get_user_input_fast(root)
            invoke_id = self._get_invoke_id_fast(root)
            message_type = self._get_message_type_fast(root)

            # Handle session efficiently
            session = self._handle_session(dialog_type, msisdn, session_id, user_input or "")
            
            # Update session with minimal dictionary operations
            session_updates = {
                'message_type': message_type,
                'remote_id': remote_id,
                'network_id': network_id,
                'user_object': user_object,
                'invoke_id': invoke_id,
                'dialog_type': dialog_type,
            }
            session.session_data.update(session_updates)
            
            if user_input:
                session.store_response('user_input', user_input)
            session.update_activity()

            # Return optimized dictionary
            return {
                "session_id": session_id,
                "remote_id": remote_id,
                "msisdn": msisdn,
                "network_id": network_id,
                "user_object": user_object,
                "invoke_id": invoke_id,
                "message_type": message_type,
                "dialog_type": dialog_type,
                "user_input": user_input,
                "raw_xml": raw_xml
            }
            
        except etree.XMLSyntaxError as e:
            return self._create_error_dict("XML_SYNTAX_ERROR", str(e))
        except Exception as e:
            logging.error(f"Parse error: {e}")
            return self._create_error_dict("PARSE_FAILURE", str(e))

    def getResponse(self, msisdn: str, text: str, end_or_not: bool) -> str:
        """Generate XML response with optimized string building"""
        session = self.session_manager.get_session(msisdn)
        if session is None:
            raise ValueError(f"No active session found for MSISDN: {msisdn}")
        
        # Use fast lookup for response message type
        message_type = session.session_data.get('message_type', 'processUnstructuredSSRequest_Request')
        dialog_action = "End" if end_or_not else "Continue"
        response_message_type = self._get_response_message_type_fast(message_type, dialog_action)

        # Build attributes efficiently
        dialog_attrs = {
            "type": dialog_action,
            "localId": session.session_id,
            "remoteId": session.session_data.get('remote_id', ''),
            "appCntx": "networkUnstructuredSsContext_version2",
            "networkId": session.session_data.get('network_id', '0'),
            "mapMessagesSize": "1",
            "returnMessageOnError": "false"
        }

        if end_or_not:
            dialog_attrs["prearrangedEnd"] = "false"
        elif session.session_data.get('user_object'):
            dialog_attrs["userObject"] = session.session_data['user_object']

        # Build XML efficiently
        root = ET.Element("dialog", attrib=dialog_attrs)
        response_attrs = {
            "invokeId": session.session_data.get('invoke_id', '1'),
            "dataCodingScheme": "15",
            "string": text
        }

        response_elem = ET.SubElement(root, response_message_type, attrib=response_attrs)
        
        # Add MSISDN only when required
        if response_message_type in {"processUnstructuredSSRequest_Response", "unstructuredSSRequest_Request"}:
            ET.SubElement(response_elem, "msisdn", attrib={
                "number": session.msisdn,
                "nai": "international_number",
                "npi": "ISDN"
            })

        # Generate response string
        xml_str = ET.tostring(root, encoding="unicode")
        response = f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'
        
        if end_or_not:
            self.session_manager.end_session(session)
        
        return response

    # Optimized helper methods
    def _get_network_id_fast(self, root) -> str:
        """Fast network ID extraction"""
        result = self._XPATH_NETWORK_ID(root)
        return result[0] if result else "0"

    def _extract_msisdn_fast(self, root, dialog_type: str) -> str:
        """Optimized MSISDN extraction with early termination"""
        for extractor in self._msisdn_extractors:
            msisdn = extractor(root)
            if msisdn and msisdn != "*":
                return msisdn
        
        raise ValueError(f"MSISDN not found in XML for dialog type '{dialog_type}'")

    def _extract_begin_msisdn(self, root) -> Optional[str]:
        result = self._XPATH_BEGIN_MSISDN(root)
        return result[0] if result else None

    def _extract_origination_ref(self, root) -> Optional[str]:
        result = self._XPATH_ORIGINATION_REF(root)
        return result[0] if result else None

    def _extract_remote_gt_digits(self, root) -> Optional[str]:
        result = self._XPATH_REMOTE_GT_DIGITS(root)
        return result[0] if result else None

    def _extract_destination_ref(self, root) -> Optional[str]:
        result = self._XPATH_DESTINATION_REF(root)
        return result[0] if result else None

    def _extract_msisdn_all(self, root) -> Optional[str]:
        result = self._XPATH_MSISDN_ALL(root)
        return result[0] if result else None

    def _extract_gt_digits_all(self, root) -> Optional[str]:
        result = self._XPATH_GT_DIGITS_ALL(root)
        return result[0] if result else None

    def _get_user_input_fast(self, root) -> Optional[str]:
        """Fast user input extraction"""
        request_input = self._XPATH_USER_INPUT_REQUEST(root)
        if request_input:
            return request_input[0]
        
        response_input = self._XPATH_USER_INPUT_RESPONSE(root)
        return response_input[0] if response_input else None

    def _get_invoke_id_fast(self, root) -> Optional[str]:
        """Fast invoke ID extraction"""
        request_id = self._XPATH_INVOKE_ID_REQUEST(root)
        if request_id:
            return request_id[0]
        
        response_id = self._XPATH_INVOKE_ID_RESPONSE(root)
        return response_id[0] if response_id else None

    def _get_message_type_fast(self, root) -> str:
        """Fast message type detection"""
        request_types = self._XPATH_REQUEST_TYPES(root)
        if not request_types:
            raise ValueError("No valid USSD request type found in XML")
        
        return etree.QName(request_types[0]).localname

    def _get_response_message_type_fast(self, incoming_message_type: str, dialog_type: str) -> str:
        """Fast response message type lookup using pre-computed mapping"""
        key = (incoming_message_type, dialog_type)
        response_type = self.RESPONSE_TYPE_MAP.get(key)
        
        if response_type is None:
            raise ValueError(f"Invalid combination: {incoming_message_type} + {dialog_type}")
        
        return response_type

    def _handle_session(self, dialog_type: str, msisdn: str, session_id: str, service_code: str) -> USSDSession:
        """Efficient session handling"""
        if dialog_type == "Begin":
            return self.session_manager.create_session(msisdn, session_id, service_code, None)
        
        session = self.session_manager.get_session(msisdn)
        if session is None:
            logging.warning(f"No session for {msisdn}, creating fallback")
            return self.session_manager.create_session(msisdn, session_id, "", None)
        
        return session

    def _create_error_dict(self, error_type: str, error_message: str) -> Dict:
        """Create error dictionary with minimal allocations"""
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

    # Maintain backward compatibility
    def get_response_message_type(self, incoming_message_type: str, dialog_type: str = "Continue") -> str:
        """Backward compatibility method"""
        return self._get_response_message_type_fast(incoming_message_type, dialog_type)

    def get_user_input(self, root) -> Optional[str]:
        """Backward compatibility method"""
        return self._get_user_input_fast(root)

    def get_message_type(self, root) -> str:
        """Backward compatibility method"""
        return self._get_message_type_fast(root)

    def _get_session_id(self, root) -> str:
        """Backward compatibility method"""
        return root.get("localId", "0")

    def _get_network_id(self, root) -> str:
        """Backward compatibility method"""
        return self._get_network_id_fast(root)

    def _extract_msisdn(self, root, dialog_type: str) -> str:
        """Backward compatibility method"""
        return self._extract_msisdn_fast(root, dialog_type)

    def _get_xpath_value(self, root, key: str, default: str = "*") -> str | None:
        """Backward compatibility method - deprecated"""
        logging.warning("_get_xpath_value is deprecated, use specific extraction methods")
        return None

    def _get_invoke_id(self, root) -> Optional[str]:
        """Backward compatibility method"""
        return self._get_invoke_id_fast(root)

    def _build_error_dict(self, error_type: str, error_message: str) -> Dict:
        """Backward compatibility method"""
        return self._create_error_dict(error_type, error_message)