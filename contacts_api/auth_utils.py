from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from bcrypt import hashpw, gensalt, checkpw


SECRET_KEY = "SUPER_SECRET_KEY_DONT_SHARE"
ALGORITHM = "HS256"



def get_password_hash(password: str) -> str:
    return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))



def create_token(data: dict, expires_delta: Optional[timedelta] = None, token_type: str = "access"):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + (timedelta(minutes=15) if token_type == "access" else timedelta(days=7))

    to_encode.update({"exp": expire, "scope": token_type})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)