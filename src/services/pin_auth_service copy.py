
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
from src.db.db_config import find_user_by_phone_and_user_type_and_active_true_and_deleted_false
import re
import logging
# import jwt
from datetime import datetime, timedelta
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enums
class ResponseCode(Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class UserType(Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    CORP = "CORP"

class CorpType(Enum):
    SYSTEM = "SYSTEM"
    REGULAR = "REGULAR"

# Data Classes
@dataclass
class LoginRequest:
    username: str
    password: str = ""
    
    def set_username(self, username: str):
        self.username = username

@dataclass
class LoginResponse:
    response_code: ResponseCode
    message: str
    token: Optional[str] = None
    user_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "response_code": self.response_code.value,
            "message": self.message,
            "token": self.token,
            "user_data": self.user_data
        }

@dataclass
class BaseUser:
    id: int
    username: str
    email: str
    phone: str
    user_type: UserType
    active: bool = True
    deleted: bool = False

@dataclass
class CorpUser(BaseUser):
    corp_type: CorpType = CorpType.REGULAR



def generate_jwt_token(user_id: str, user_type: str, otp: str, secret_key: str) -> str:
    """
    Generate a JWT token for a user with specified claims.
    
    Args:
        user_id (str): The user's ID.
        user_type (str): The user's type (e.g., 'AGENT', 'CORPORATE').
        otp (str): One-time password or related value for 'kuttyChatan' claim.
        secret_key (str): Secret key for signing the token.
    
    Returns:
        str: The generated JWT token.
    """
    # Define claims
    claims = {
        "userId": str(user_id),
        "userType": user_type,
        "kuttyChatan": otp,
        "sub": str(user_id),  # Subject
        "iat": datetime.utcnow(),  # Issued at
        "exp": datetime.utcnow() + timedelta(hours=1)  # Expiration (1 hour)
    }
    
    # Encode the token
    token = jwt.encode(
        payload=claims,
        key=secret_key,
        algorithm="HS256"
    )
    
    return token

def generate_refresh_token(access_token: str, secret_key: str) -> str:
    """
    Generate a refresh JWT token based on an existing access token.
    
    Args:
        access_token (str): The existing JWT access token.
        secret_key (str): Secret key for verifying and signing the token.
    
    Returns:
        str: The generated refresh JWT token.
    """
    try:
        # Decode the existing token to extract claims
        decoded = jwt.decode(access_token, secret_key, algorithms=["HS256"])
        
        # Create new claims for refresh token
        claims = {
            "userId": decoded["userId"],
            "userType": decoded["userType"],
            "kuttyChatan": decoded["kuttyChatan"],
            "sub": decoded["userId"],
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        
        # Encode the refresh token
        token = jwt.encode(
            payload=claims,
            key=secret_key,
            algorithm="HS256"
        )
        
        return token
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid access token: {str(e)}")

def validate_phone_number(phone: str, pin:str) -> bool:
    find_user_by_phone_and_user_type_and_active_true_and_deleted_false(phone,
                                                                        "USER"
                                                                          )
