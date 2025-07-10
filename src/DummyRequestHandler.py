from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse, parse_qs
import signal
import sys

class DummyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle_request()
    
    def do_POST(self):
        self._handle_request()
    
    def do_PUT(self):
        self._handle_request()
    
    def do_DELETE(self):
        self._handle_request()
    
    def do_PATCH(self):
        self._handle_request()
    
    def do_HEAD(self):
        self._handle_request()
    
    def do_OPTIONS(self):
        self._handle_request()
    
    def _handle_request(self):
        # Initialize response payload
        response = {
            'status': 'success',
            'message': 'Request received',
            'path': self.path,
            'method': self.command,
            'query_params': {},
            'post_data': {}
        }

        # Parse query parameters from URL
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        response['query_params'] = {k: v if len(v) > 1 else v[0] for k, v in query_params.items()}

        # Parse POST data if present
        if self.command in ['POST', 'PUT', 'PATCH']:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                try:
                    post_data = self.rfile.read(content_length).decode('utf-8')
                    # Attempt to parse as JSON, otherwise return as raw string
                    try:
                        response['post_data'] = json.loads(post_data)
                    except json.JSONDecodeError:
                        response['post_data'] = post_data
                except Exception as e:
                    response['post_data'] = {'error': f'Failed to read POST data: {str(e)}'}

        # Print request details
        print(f"\n{'='*60}")
        print(f"REQUEST RECEIVED:")
        print(f"{'='*60}")
        print(f"Method: {self.command}")
        print(f"Path: {self.path}")
        print(f"Query Parameters: {response['query_params']}")
        print(f"Headers:")
        for header, value in self.headers.items():
            print(f"  {header}: {value}")
        if response['post_data']:
            print(f"POST Data: {response['post_data']}")
        
        # Response headers
        response_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.dummy.token'
        }
        
        # Send response
        self.send_response(200)
        for header, value in response_headers.items():
            self.send_header(header, value)
        self.end_headers()
        
        # Response body
        response_body = json.dumps(response, indent=2)
        self.wfile.write(response_body.encode('utf-8'))
        
        # Print response details
        print(f"\nRESPONSE SENT:")
        print(f"Status: 200 OK")
        print(f"Headers:")
        for header, value in response_headers.items():
            print(f"  {header}: {value}")
        print(f"Body: {response_body}")
        print(f"{'='*60}")

def signal_handler(sig, frame):
    print('\nKeyboard interrupt received, shutting down the server.')
    sys.exit(0)

def run_server(port=8080):
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, DummyRequestHandler)
    print(f"Starting dummy server on port {port}...")
    print(f"Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nKeyboard interrupt received, shutting down the server.')
        httpd.server_close()

if __name__ == '__main__':
    run_server()