import requests
import logging
import json
import hashlib
import hmac
import threading
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict

# Thread-safe token manager
class AuthTokenManager:
    """Thread-safe manager for authentication tokens"""
    _instance = None
    _lock = threading.Lock()
    _token_lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern implementation"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._token = None
        return cls._instance
    
    def set_token(self, token: str):
        """Set the current authentication token"""
        with self._token_lock:
            self._token = token
    
    def get_token(self) -> Optional[str]:
        """Get the current authentication token"""
        with self._token_lock:
            return self._token
    
    def clear_token(self):
        """Clear the current authentication token"""
        with self._token_lock:
            self._token = None

# Global token manager instance
token_manager = AuthTokenManager()

class PinAuthService:
    """Secure PIN authentication service with token management"""
    
    def __init__(self, 
                 verify_url: str,
                 api_key: str,
                 lockout_threshold: int = 3, 
                 lockout_duration: int = 5,
                 timeout: int = 5):
        """
        Initialize PIN authentication service
        
        Args:
            verify_url: URL for PIN verification API
            api_key: Secret key for API authentication
            lockout_threshold: Failed attempts before lockout (default: 3)
            lockout_duration: Lockout duration in minutes (default: 5)
            timeout: API timeout in seconds (default: 5)
        """
        self.verify_url = verify_url
        self.api_key = api_key
        self.lockout_threshold = lockout_threshold
        self.lockout_duration = timedelta(minutes=lockout_duration)
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        self.failed_attempts = {}
        self.logger.info("PinAuthService initialized with URL: %s", verify_url)
    
    def _generate_api_signature(self, payload: Dict) -> str:
        """
        Generate HMAC signature for API request
        
        Args:
            payload: Request payload to sign
            
        Returns:
            str: HMAC-SHA256 signature
        """
        sorted_payload = json.dumps(payload, sort_keys=True)
        return hmac.new(
            self.api_key.encode('utf-8'),
            sorted_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def verify_pin(self, msisdn: str, pin: str) -> Tuple[bool, str]:
        """
        Verify PIN by calling web service and store token
        
        Args:
            msisdn: User's phone number
            pin: PIN to verify
            
        Returns:
            Tuple: (success: bool, message: str)
        """
        # Check lockout status
        locked, message = self.is_account_locked(msisdn)
        if locked:
            self.logger.warning("Account locked for %s: %s", msisdn, message)
            return False, message
        
        # Validate PIN format
        if not pin or len(pin) != 6 or not pin.isdigit():
            return False, "Invalid PIN format"
        
        # Prepare API request
        payload = {
            "msisdn": msisdn,
            "pin": pin,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-API-Signature": self._generate_api_signature(payload)
        }
        
        try:
            # Call verification API
            self.logger.debug("Calling PIN verification API: %s", self.verify_url)
            response = requests.post(
                self.verify_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            # Handle successful response
            if response.status_code == 200:
                # Extract token from Authorization header
                auth_header = response.headers.get("Authorization", "")
                if auth_header.startswith("Bearer "):
                    token = auth_header.split("Bearer ")[1].strip()
                    token_manager.set_token(token)
                    self.logger.info("Token stored for %s", msisdn)
                
                # Reset failed attempts on success
                if msisdn in self.failed_attempts:
                    del self.failed_attempts[msisdn]
                
                return True, "Authentication successful"
            
            # Handle specific error cases
            elif response.status_code == 400:
                error = "Invalid request format"
            elif response.status_code == 401:
                self._record_failed_attempt(msisdn)
                error = "Invalid PIN"
            elif response.status_code == 403:
                self._record_failed_attempt(msisdn, lock=True)
                error = "Account locked"
            elif response.status_code == 404:
                error = "User not found"
            else:
                error = f"Unexpected status: {response.status_code}"
            
            self.logger.warning("PIN verification failed for %s: %s", msisdn, error)
            return False, error
        
        except requests.exceptions.Timeout:
            error = "Verification service timed out"
            self.logger.error(error)
            return False, error
        except requests.exceptions.RequestException as e:
            error = f"API call failed: {str(e)}"
            self.logger.error(error)
            return False, "Service unavailable"
    
    def is_account_locked(self, msisdn: str) -> Tuple[bool, str]:
        """
        Check if account is locked due to failed attempts
        
        Args:
            msisdn: User's phone number
            
        Returns:
            Tuple: (is_locked: bool, message: str)
        """
        if msisdn not in self.failed_attempts:
            return False, ""
        
        attempts, lock_time = self.failed_attempts[msisdn]
        
        # Check if still in lockout period
        if datetime.now() - lock_time < self.lockout_duration:
            remaining_min = (lock_time + self.lockout_duration - datetime.now()).seconds // 60
            message = f"Account locked. Try again in {remaining_min} minutes"
            return True, message
        
        # Clear expired lockout
        if attempts >= self.lockout_threshold:
            del self.failed_attempts[msisdn]
            self.logger.info("Lock expired for %s", msisdn)
        
        return False, ""
    
    def _record_failed_attempt(self, msisdn: str, lock: bool = False):
        """
        Track failed PIN attempts and lock if threshold reached
        
        Args:
            msisdn: User's phone number
            lock: Whether to immediately lock account
        """
        now = datetime.now()
        
        if msisdn not in self.failed_attempts:
            self.failed_attempts[msisdn] = [1, now]
            return
        
        attempts, last_time = self.failed_attempts[msisdn]
        
        # Reset if last attempt was long ago
        if now - last_time > timedelta(minutes=10):
            self.failed_attempts[msisdn] = [1, now]
        else:
            new_attempts = attempts + 1
            self.failed_attempts[msisdn] = [new_attempts, now]
            
            # Lock account if threshold reached or forced
            if lock or new_attempts >= self.lockout_threshold:
                self.logger.warning("Account locked for %s after %d failed attempts", 
                                   msisdn, new_attempts)
                # Update lock time
                self.failed_attempts[msisdn][1] = now
    
    def get_current_token(self) -> Optional[str]:
        """
        Get the current authentication token
        
        Returns:
            str: Current bearer token or None
        """
        return token_manager.get_token()
    
    def clear_current_token(self):
        """
        Clear the current authentication token
        """
        token_manager.clear_token()
        self.logger.info("Authentication token cleared")

# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create service instance
    auth_service = PinAuthService(
        verify_url="https://auth.example.com/verify-pin",
        api_key="your-secret-api-key",
        lockout_threshold=3,
        lockout_duration=2  # 2 minutes for testing
    )
    
    # Test PIN verification
    test_msisdn = "93701234567"
    
    print("===== TEST 1: Valid PIN =====")
    success, message = auth_service.verify_pin(test_msisdn, "123456")
    print(f"Success: {success}, Message: {message}")
    print(f"Token: {token_manager.get_token()}")
    
    print("\n===== TEST 2: Invalid PIN =====")
    success, message = auth_service.verify_pin(test_msisdn, "000000")
    print(f"Success: {success}, Message: {message}")
    
    print("\n===== TEST 3: Lockout Test =====")
    for i in range(3):
        success, message = auth_service.verify_pin(test_msisdn, "wrong")
        print(f"Attempt {i+1}: Success={success}, Message={message}")
    
    print("\n===== TEST 4: Locked Account =====")
    success, message = auth_service.verify_pin(test_msisdn, "123456")
    print(f"Success: {success}, Message: {message}")
    
    print("\n===== TEST 5: Wait for Lock Expiry =====")
    print("Waiting 2 minutes for lock to expire...")
    # Simulate lock expiration by modifying time
    if test_msisdn in auth_service.failed_attempts:
        auth_service.failed_attempts[test_msisdn][1] = datetime.now() - timedelta(minutes=3)
    
    locked, message = auth_service.is_account_locked(test_msisdn)
    print(f"Account locked: {locked}, Message: {message}")
    
    print("\n===== TEST 6: Valid PIN After Lock =====")
    success, message = auth_service.verify_pin(test_msisdn, "123456")
    print(f"Success: {success}, Message: {message}")
    print(f"Token: {token_manager.get_token()}")
    
    print("\n===== TEST 7: Clear Token =====")
    auth_service.clear_current_token()
    print(f"Token after clear: {token_manager.get_token()}")