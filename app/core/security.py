import os
from datetime import datetime, timedelta, timezone
import jwt
from dotenv import load_dotenv
from fastapi import HTTPException, status

load_dotenv()

# We expect the secret key to be loaded from .env
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super_secret_temporary_key_change_me")
ALGORITHM = "HS256"

def get_expiration_minutes() -> int:
    try:
        val = os.getenv("JWT_TOKEN_EXPIRATION_IN_MINUTES", "10080")
        return int(float(val))
    except ValueError:
        return 10080

import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    # bcrypt maximum limit is 72 bytes. We encode as utf-8.
    # Front-end validation enforces a minimum password length, and we hash it safely.
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=get_expiration_minutes())
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
