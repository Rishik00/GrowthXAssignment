from fastapi import Depends, HTTPException
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY_ADMIN", "your_default_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))

# Initialize password hashing context
auth_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    """Generate a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_admin(token: str = Depends(auth_scheme)):
    """Validate and retrieve the current admin from the JWT."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin: str = payload.get("sub")
        if admin is None:
            raise credentials_exception
        return admin
    except JWTError:
        raise credentials_exception
