from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import secrets
import os

import models
from database import get_db

# Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-min-32-characters-long')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 1440))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ============================================================================
# PASSWORD HASHING
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

# ============================================================================
# TOKEN MANAGEMENT
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "sub": str(to_encode.get("sub")),  # Ensure sub is string
        "type": "access"
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_reset_token() -> str:
    """Create password reset token"""
    return secrets.token_urlsafe(32)

# ============================================================================
# USER AUTHENTICATION
# ============================================================================

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user by email or phone"""
    # Try email first
    user = db.query(models.User).filter(models.User.email == username).first()
    
    # Try phone if email not found
    if not user:
        user = db.query(models.User).filter(models.User.phone_number == username).first()
    
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    
    return user

# def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     """Get current authenticated user"""
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
    
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id: int = payload.get("sub")
#         if user_id is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception
    
#     user = db.query(models.User).filter(models.User.id == user_id).first()
#     if user is None:
#         raise credentials_exception
    
#     if not user.is_active:
#         raise HTTPException(status_code=400, detail="Inactive user")
    
#     return user
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        print(f"Token received: {token}")  # Debug
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Payload: {payload}")  # Debug
        
        user_id = payload.get("sub")
        print(f"Extracted user_id: {user_id}")  # Debug
        
        if user_id is None:
            print("user_id is None")  # Debug
            raise credentials_exception
            
        # Convert to int if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)
            
    except JWTError as e:
        print(f"JWTError: {e}")  # Debug
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    print(f"User found: {user}")  # Debug
    
    if user is None:
        print("User not found in database")  # Debug
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user

def get_current_admin(current_user: models.User = Depends(get_current_user)):
    """Require admin role"""
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user