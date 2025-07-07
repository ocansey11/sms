from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import secrets
import string

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token types
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


class SecurityManager:
    """Security utilities for password hashing and JWT token management."""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash."""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "type": TOKEN_TYPE_ACCESS,
            "iat": datetime.utcnow()
        })
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create JWT refresh token (longer expiration)."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=30)  # 30 days for refresh token
        
        to_encode.update({
            "exp": expire,
            "type": TOKEN_TYPE_REFRESH,
            "iat": datetime.utcnow()
        })
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = TOKEN_TYPE_ACCESS) -> dict:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            # Check token type
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Check expiration
            exp = payload.get("exp")
            if exp is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token missing expiration",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            if datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return payload
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def generate_reset_token(length: int = 32) -> str:
        """Generate secure random token for password reset."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """Validate password meets security requirements."""
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*(),.?\":{}|<>" for c in password)
        
        return has_upper and has_lower and has_digit and has_special


# Create security manager instance
security = SecurityManager()
