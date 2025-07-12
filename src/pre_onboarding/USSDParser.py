from lxml import etree
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class USSDParser:
    """Minimal USSD XML parser for AWCC compliance"""
    def __init__(self, session_manager=None):
        self.session_manager = session_manager

    def parse_request(self, xml_str: str) -> Dict[str, str]:
        """Parse USSD XML request to extract minimal fields"""
        try:
            root = etree.fromstring(xml_str)
            parsed_data = {
                "msisdn": root.findtext("msisdn") or "",
                "service_code": root.findtext("serviceCode") or "*220#",
                "user_input": root.findtext("userInput") or "",
                "dialog_type": root.get("type", "Begin")
            }
            logger.debug(f"Parsed USSD request: {parsed_data}")
            return parsed_data
        except etree.XMLSyntaxError as e:
            logger.error(f"Failed to parse USSD XML: {e}")
            return {"msisdn": "", "service_code": "", "user_input": "", "dialog_type": "End"}

    def getResponse(self, msisdn: str, prompt: str, end_session: bool) -> str:
        """Generate AWCC-compliant USSD XML response"""
        dialog_type = "End" if end_session else "Continue"
        xml = (
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<dialog type="{dialog_type}">\n'
            f'  <msisdn>{msisdn}</msisdn>\n'
            f'  <prompt>{prompt}</prompt>\n'
            f'</dialog>'
        )
        return xml