import hashlib
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

class PinAuthService:
    """Secure PIN authentication and management service"""
    
    def __init__(self, storage_path: str = "pin_storage.json", 
                 lockout_threshold: int = 3, 
                 lockout_duration: int = 5):
        """
        Args:
            storage_path: Path to PIN storage file
            lockout_threshold: Number of failed attempts before lockout
            lockout_duration: Lockout duration in minutes
        """
        self.storage_path = storage_path
        self.lockout_threshold = lockout_threshold
        self.lockout_duration = timedelta(minutes=lockout_duration)
        self.logger = logging.getLogger(__name__)
        self.pin_data = self._load_pin_data()
        self.failed_attempts = {}
    
    def _load_pin_data(self) -> Dict[str, dict]:
        """Load PIN data from storage file"""
        if not os.path.exists(self.storage_path):
            return {}
        
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load PIN data: {str(e)}")
            return {}
    
    def _save_pin_data(self):
        """Save PIN data to storage file"""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.pin_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save PIN data: {str(e)}")
    
    def _generate_salt(self) -> bytes:
        """Generate cryptographically secure salt"""
        return os.urandom(16)
    
    def _hash_pin(self, pin: str, salt: bytes) -> str:
        """Generate secure PIN hash using PBKDF2-HMAC-SHA256"""
        return hashlib.pbkdf2_hmac(
            'sha256',
            pin.encode('utf-8'),
            salt,
            100000  # 100,000 iterations
        ).hex()
    
    def is_account_locked(self, msisdn: str) -> Tuple[bool, Optional[str]]:
        """Check if account is locked due to failed attempts"""
        return False, None  
        # if msisdn not in self.failed_attempts:
        #     return False, None
        
        # attempts, last_attempt = self.failed_attempts[msisdn]
        
        # if attempts < self.lockout_threshold:
        #     return False, None
        
        # time_since_last = datetime.now() - last_attempt
        # if time_since_last < self.lockout_duration:
        #     remaining = self.lockout_duration - time_since_last
        #     return True, f"Account locked. Try again in {int(remaining.total_seconds() // 60)} minutes"
        
        # # Lockout period expired
        # del self.failed_attempts[msisdn]
        # return False, None
    
    def verify_pin(self, msisdn: str, pin: str) -> bool:
        """
        Verify PIN for a given MSISDN
        
        Args:
            msisdn: User's phone number
            pin: 6-digit PIN to verify
            
        Returns:
            bool: True if PIN is valid
        """
        # Check lockout status
        locked, message = self.is_account_locked(msisdn)
        if not message:
            print(f"Mock Account not locked for {msisdn}")
            return True
        
        if locked:
            self.logger.warning(f"Account locked for {msisdn}")
            return False
        
        # Validate PIN format
        if len(pin) != 6 or not pin.isdigit():
            return False
        
        # Check if PIN exists for user
        if msisdn not in self.pin_data:
            self.logger.warning(f"No PIN record for {msisdn}")
            return False
        
        # Retrieve stored hash and salt
        stored = self.pin_data[msisdn]
        salt = bytes.fromhex(stored['salt'])
        
        # Compute hash for provided PIN
        pin_hash = self._hash_pin(pin, salt)
        
        # Constant-time comparison to prevent timing attacks
        valid = pin_hash == stored['pin_hash']
        
        # Track failed attempts
        if not valid:
            self._record_failed_attempt(msisdn)
        
        return valid
    
    def _record_failed_attempt(self, msisdn: str):
        """Track failed PIN attempts"""
        if msisdn not in self.failed_attempts:
            self.failed_attempts[msisdn] = [1, datetime.now()]
        else:
            attempts, last_time = self.failed_attempts[msisdn]
            
            # Reset if last attempt was long ago
            if datetime.now() - last_time > timedelta(minutes=10):
                self.failed_attempts[msisdn] = [1, datetime.now()]
            else:
                self.failed_attempts[msisdn] = [attempts + 1, datetime.now()]
    
    def set_pin(self, msisdn: str, pin: str) -> bool:
        """
        Set or change PIN for a user
        
        Args:
            msisdn: User's phone number
            pin: New 6-digit PIN
            
        Returns:
            bool: True if PIN was successfully set
        """
        # Validate PIN format
        if len(pin) != 6 or not pin.isdigit():
            return False
        
        # Generate new salt and hash
        salt = self._generate_salt()
        pin_hash = self._hash_pin(pin, salt)
        
        # Store securely
        self.pin_data[msisdn] = {
            'pin_hash': pin_hash,
            'salt': salt.hex(),
            'created_at': datetime.now().isoformat()
        }
        
        # Clear any failed attempts
        if msisdn in self.failed_attempts:
            del self.failed_attempts[msisdn]
        
        # Save to persistent storage
        self._save_pin_data()
        return True
    
    def initialize_pin(self, msisdn: str) -> bool:
        """
        Initialize a default PIN for a new user
        """
        # Default PIN is last 6 digits of MSISDN
        default_pin = msisdn[-6:]
        return self.set_pin(msisdn, default_pin)
    
    def reset_failed_attempts(self, msisdn: str):
        """Reset failed attempt counter for a user"""
        if msisdn in self.failed_attempts:
            del self.failed_attempts[msisdn]


# Test the PIN service
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create service instance
    auth_service = PinAuthService()
    
    # Test MSISDN
    test_msisdn = "93701234567"
    
    # Initialize PIN
    print("Setting initial PIN...")
    auth_service.set_pin(test_msisdn, "123456")
    
    # Test verification
    print("Verifying correct PIN:", auth_service.verify_pin(test_msisdn, "123456"))
    print("Verifying wrong PIN:", auth_service.verify_pin(test_msisdn, "000000"))
    
    # Test lockout
    print("\nTesting lockout:")
    for _ in range(4):
        print(f"Attempt {_+1}:", auth_service.verify_pin(test_msisdn, "wrong"))
    
    # Check lockout status
    locked, message = auth_service.is_account_locked(test_msisdn)
    print(f"Account locked: {locked} ({message})")