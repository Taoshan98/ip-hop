from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union
from jose import jwt, JWTError
import bcrypt
from cryptography.fernet import Fernet
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7) # 7 days

SECRET_KEY = os.getenv("SECRET_KEY")
if not ENCSECRET_KEYRYPTION_KEY:
    raise ValueError("SECRET_KEY environment variable is not set. This is required to secure credentials.")

# Fernet key for encrypting credentials in DB
# In production, this must be loaded from env and consistent
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY environment variable is not set. This is required to secure credentials.")

fernet = Fernet(ENCRYPTION_KEY.encode())

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"sub": str(subject), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token. Returns None if invalid/expired."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def encrypt_credentials(credentials: dict) -> str:
    """Encrypts a dictionary of credentials to a string."""
    json_str = json.dumps(credentials)
    return fernet.encrypt(json_str.encode()).decode()

def decrypt_credentials(encrypted_str: str) -> dict:
    """Decrypts a string back to a credentials dictionary."""
    json_str = fernet.decrypt(encrypted_str.encode()).decode()
    return json.loads(json_str)

