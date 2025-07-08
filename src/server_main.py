import http.server
import socketserver
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs
from src.ussd_handler import USSDGatewayHandler
from src.menu.graph.demo_menu_config import config

config_mapping = {
    "*220#": config,  # Default config from demo_menu_config.py
    "*220#1": config  # Example: same config, but could be config2
    # Add more mappings as needed, e.g., "*222#1": config2
}

class XMLHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler that processes XML requests and responses"""
    
    def do_POST(self):
        """Handle POST requests with XML data"""
        try:
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            
            # Read XML data
            xml_data = self.rfile.read(content_length).decode('utf-8')
            resp = self.server.handler.handle_request(xml_data)
            print(f"Req --> :\n{xml_data} \n \n Resp --> :\n{resp}")
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/xml')
            self.send_header('Content-Length', str(len(resp)))
            self.end_headers()
            self.wfile.write(resp.encode('utf-8'))
            
        except ET.ParseError as e:
            self.send_error(400, f"Invalid XML: {e}")
        except Exception as e:
            self.send_error(500, f"Server error: {e}")
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        print(f"GET request: {self.path}")
        print(f"Query params: {query_params}")
        
        # Generate XML response
        response_xml = self.generate_xml_response(parsed_url.path, query_params)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/xml')
        self.send_header('Content-Length', str(len(response_xml)))
        self.end_headers()
        self.wfile.write(response_xml.encode('utf-8'))
    
    def process_xml(self, root):
        """Process incoming XML and return response XML"""
        # Extract data from incoming XML
        # Customize this based on your XML structure
        
        # Example: Echo back with modified content
        response_root = ET.Element("response")
        status_elem = ET.SubElement(response_root, "status")
        status_elem.text = "success"
        
        # Add original data
        original_elem = ET.SubElement(response_root, "original")
        original_elem.append(root)
        
        # Add timestamp
        import time
        timestamp_elem = ET.SubElement(response_root, "timestamp")
        timestamp_elem.text = str(int(time.time()))
        
        return ET.tostring(response_root, encoding='unicode')
    
    def generate_xml_response(self, path, params):
        """Generate XML response for GET requests"""
        root = ET.Element("response")
        
        path_elem = ET.SubElement(root, "path")
        path_elem.text = path
        
        if params:
            params_elem = ET.SubElement(root, "parameters")
            for key, values in params.items():
                param_elem = ET.SubElement(params_elem, "parameter")
                param_elem.set("name", key)
                param_elem.text = ", ".join(values)
        
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{ET.tostring(root, encoding="unicode")}'
    
    def log_message(self, format, *args):
        """Override to customize logging"""
        print(f"[{self.address_string()}] {format % args}")

class XMLHTTPServer:
    """XML HTTP Server wrapper"""
    def __init__(self, port=8080, host='localhost'):
        self.port = port
        self.host = host
        self.server = None
        # Initialize handler once here
        self.handler = USSDGatewayHandler(config_mapping)
    
    def start(self):
        """Start the server"""
        try:
            self.server = socketserver.TCPServer((self.host, self.port), XMLHTTPRequestHandler)
            # Make handler available to request handler instances
            self.server.handler = self.handler
            print(f"XML HTTP Server started on {self.host}:{self.port}")
            print(f"Access at: http://{self.host}:{self.port}")
            print("Press Ctrl+C to stop the server")
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            self.stop()
        except Exception as e:
            print(f"Error starting server: {e}")
    
    def stop(self):
        """Stop the server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("Server stopped")

# Example usage
if __name__ == "__main__":
    # Create and start server on custom port
    server = XMLHTTPServer(port=3214, host='0.0.0.0')  # Listen on all interfaces
    server.start()
    
    # Alternative: Quick start with default settings
    # server = XMLHTTPServer()
    # server.start()