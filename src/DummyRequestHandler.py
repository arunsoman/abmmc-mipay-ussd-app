from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse, parse_qs
import signal
import sys
import random
import string

class DummyRequestHandler(BaseHTTPRequestHandler):
    def _send_response(self, response_code, data):
        self.send_response(response_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _generate_receipt_number(self):
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def _log_request(self, method, path, query_params, body=None):
        print(f"--- Unmatched Request ---")
        print(f"Method: {method}")
        print(f"Path: {path}")
        print(f"Query Parameters: {query_params}")
        print(f"Headers: {dict(self.headers)}")
        if body:
            print(f"Body: {body}")
        print("------------------------")


    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        if path == "/ts/api/transaction-services/findWithdrawalReq":
            # getCashOutRequests: Return array of withdrawal requests
            data = [
                {"id": 1, "amount": 1000, "status": "PENDING"},
                {"id": 2, "amount": 2500, "status": "PENDING"}
            ]
            self._send_response(200, {"responseCode": 200, "data": data, "error": None})

        elif path == "/tms/serviceDetail/awcc/bundlePacks":
            # GetBundleListAPI: Return data and voice bundles
            data = {
                "dataBundle": [
                    {"name": "2.5GB", "price": 280},
                    {"name": "6GB", "price": 450}
                ],
                "voiceBundle": [
                    {"name": "200 Minutes", "price": 50},
                    {"name": "550 Minutes", "price": 100}
                ]
            }
            self._send_response(200, {"responseCode": 200, "data": data, "error": None})

        elif path == "/um/bank/accounts":
            # GetLinkedBankAccountsAPI: Return array of bank accounts
            data = [
                {"account_id": "1234567890", "bank": "Maiwand", "balance": 5000},
                {"account_id": "0987654321", "bank": "Azizi", "balance": 3000}
            ]
            self._send_response(200, {"responseCode": 200, "data": data, "error": None})

        elif path == "/ts/api/transaction-services/getFilteredHistory":
            # GetTransactionHistory: Require walletNo, trxnType, fromDate, toDate
            required_params = ["walletNo", "trxnType", "fromDate", "toDate"]
            if all(param in query_params for param in required_params):
                data = [
                    {"id": 1, "amount": 500, "date": query_params["fromDate"][0], "type": query_params["trxnType"][0]},
                    {"id": 2, "amount": 1000, "date": query_params["toDate"][0], "type": query_params["trxnType"][0]}
                ]
                self._send_response(200, {"responseCode": 200, "data": data, "error": None})
            else:
                self._send_response(400, {"responseCode": 400, "error": "Missing query parameters", "data": None})

        elif path == "/ts/api/transaction-services/getFinalAmount":
            # GetFinalAmountAPI: Require serviceName, channel, amount, walletNo
            required_params = ["serviceName", "channel", "amount", "walletNo"]
            if all(param in query_params for param in required_params):
                amount = int(query_params["amount"][0])
                data = {"amount": amount + 50, "fee": 50, "service": query_params["serviceName"][0]}
                self._send_response(200, {"responseCode": 200, "data": data, "error": None})
            else:
                self._send_response(400, {"responseCode": 400, "error": "Missing query parameters", "data": None})

        elif path == "/api/bank_balance":
            # Generic bank balance endpoint
            if "bank" in query_params:
                data = {"balance": 10000, "status": "SUCCESS", "bank": query_params["bank"][0]}
                self._send_response(200, {"responseCode": 200, "data": data, "error": None})
            else:
                self._send_response(400, {"responseCode": 400, "error": "Missing bank parameter", "data": None})

        else:
            # Unmatched path: Log request and return dummy response
            self._log_request("GET", path, query_params)
            self._send_response(200, {"status": "success", 
                                      "auth":"SADDASDASDASDSD",
                                      "Authentication": "Sadasdasdasasasdsad"})

    def do_POST(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode("utf-8")
        try:
            payload = json.loads(post_data) if post_data else {}
        except json.JSONDecodeError:
            payload = post_data  # Log raw body if not JSON
            self._send_response(400, {"responseCode": 400, "error": "Invalid JSON payload", "data": None})
            return

        if path == "/tms/api/tms/router/basic":
            # StockTransferAPI, PayBreshnaBillAPI, transfer_menu, topup_self, topup_others
            required_fields = ["initiator", "context"]
            if all(field in payload for field in required_fields) and "SERVICE_NAME" in payload["context"]:
                service_name = payload["context"]["SERVICE_NAME"]
                if service_name == "BRESHNA_BILL":
                    # PayBreshnaBillAPI
                    if all(key in payload["context"] for key in ["accNo", "TransactionPin", "AMOUNT"]):
                        data = {"status": "S", "receipt_number": f"BR{self._generate_receipt_number()}"}
                        self._send_response(200, {"responseCode": 200, "data": data, "error": None})
                    else:
                        self._send_response(400, {"responseCode": 400, "error": "Missing accNo, TransactionPin, or AMOUNT", "data": None})
                else:
                    # StockTransferAPI, transfer_menu, topup_self, topup_others
                    data = {"receipt_number": f"ST{self._generate_receipt_number()}"}
                    self._send_response(200, {"responseCode": 200, "data": data, "error": None})
            else:
                self._send_response(400, {"responseCode": 400, "error": "Missing initiator or context", "data": None})

        elif path == "/aaa/USSDLogin":
            self._send_response(200, {"responseCode": 200, "data": {"auth_token": "-500-mocked-by dummy server"}, "error": None})

        elif path == "/api/pwd/update":
            # change_pin
            required_fields = ["old_pin", "new_pin", "confirm_pin"]
            if all(field in payload for field in required_fields):
                data = {"receipt_number": f"PW{self._generate_receipt_number()}"}
                self._send_response(200, {"responseCode": 200, "data": data, "error": None})
            else:
                self._send_response(400, {"responseCode": 400, "error": "Missing pin fields", "data": None})

        elif path in ["/api/link_bank", "/api/transfer_bank", "/api/transfer_from_bank"]:
            # Generic bank endpoints
            if "bank" in payload:
                data = {"receipt_number": f"BK{self._generate_receipt_number()}"}
                self._send_response(200, {"responseCode": 200, "data": data, "error": None})
            else:
                self._send_response(400, {"responseCode": 400, "error": "Missing bank parameter", "data": None})

        elif path == "/api/pay_bill":
            # delight_bill
            if "provider" in payload and "account_id" in payload:
                data = {"receipt_number": f"BL{self._generate_receipt_number()}"}
                self._send_response(200, {"responseCode": 200, "data": data, "error": None})
            else:
                self._send_response(400, {"responseCode": 400, "error": "Missing provider or account_id", "data": None})

        elif path == "/api/buy_bundle":
            # data_bundle, voice_bundle
            if "bundle_type" in payload and "option" in payload:
                data = {"receipt_number": f"BD{self._generate_receipt_number()}"}
                self._send_response(200, {"responseCode": 200, "data": data, "error": None})
            else:
                self._send_response(400, {"responseCode": 400, "error": "Missing bundle_type or option", "data": None})

        else:
            # Unmatched path: Log request and return dummy response
            self._log_request("POST", path, query_params, payload)
            self._send_response(200, {"stat": "success"})
    
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