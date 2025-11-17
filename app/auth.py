"""
Authentication utilities for SoSens - FIXED VERSION
Proper JWT token handling with string subject
"""

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import secrets

from database import get_db
import models
from config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme - tokenUrl must match your login endpoint
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/auth/login",
    description="Enter the access token returned from login endpoint"
)

# ============================================================================
# PASSWORD FUNCTIONS
# ============================================================================

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

# ============================================================================
# AUTHENTICATION
# ============================================================================

def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    """
    Authenticate user by email or phone number.
    Supports flexible login with either email or phone.
    
    Args:
        db: Database session
        username: Email or phone number
        password: Plain text password
    
    Returns:
        User object if authenticated, None otherwise
    """
    
    # Try to find user by email OR phone number
    user = db.query(models.User).filter(
        (models.User.email == username) | (models.User.phone_number == username)
    ).first()
    
    # User not found
    if not user:
        return None
    
    # Verify password
    if not verify_password(password, user.hashed_password):
        return None
    
    return user

# ============================================================================
# TOKEN FUNCTIONS - FIXED
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    
    IMPORTANT: The "sub" (subject) must be a STRING, not an integer!
    This is why we were getting "Subject must be a string" error.
    
    Args:
        data: Dictionary containing token claims (must include "sub" for user_id)
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token string
    """
    
    to_encode = data.copy()
    
    # FIXED: Convert user_id to string if it's an integer
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    print(f"DEBUG: Creating token with sub={to_encode.get('sub')} (type: {type(to_encode.get('sub'))})")
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def create_reset_token() -> str:
    """Create secure password reset token"""
    return secrets.token_urlsafe(32)

# ============================================================================
# CURRENT USER FUNCTIONS
# ============================================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Get current authenticated user from JWT token.
    
    This is used as a dependency in protected endpoints.
    Swagger UI will automatically add the token when you click Authorize.
    
    Args:
        token: JWT token from Authorization header
        db: Database session
    
    Returns:
        User object if token is valid
    
    Raises:
        HTTPException 401: If token is invalid or expired
        HTTPException 403: If user account is inactive
    """
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials - invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Extract user_id from token
        # FIXED: The "sub" is now a string, convert it to int
        user_id_str: str = payload.get("sub")
        
        if user_id_str is None:
            print(f"DEBUG: Token missing 'sub' claim")
            raise credentials_exception
        
        # Convert string to integer for database query
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            print(f"DEBUG: Cannot convert sub='{user_id_str}' to int")
            raise credentials_exception
            
    except JWTError as e:
        print(f"DEBUG: JWT decode error: {e}")
        raise credentials_exception
    
    # Get user from database
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if user is None:
        print(f"DEBUG: User not found for id={user_id}")
        raise credentials_exception
    
    # Check if user account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user

def get_current_farmer(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    Verify current user is a farmer.
    Used for farmer-only endpoints.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User object if user is a farmer
    
    Raises:
        HTTPException 403: If user is not a farmer
    """
    
    if current_user.role != models.UserRole.FARMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires farmer role"
        )
    
    return current_user

def get_current_admin(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    Verify current user is an admin.
    Used for admin-only endpoints.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User object if user is an admin
    
    Raises:
        HTTPException 403: If user is not an admin
    """
    
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires admin role"
        )
    
    return current_user