from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import structlog

from app.db.database import get_async_session
from app.core.security import security
from app.db.models import User, UserRole
from app.exceptions.custom_exceptions import (
    AuthenticationException,
    AuthorizationException,
    UserNotFoundException,
    InactiveUserException
)
from app.db import crud

logger = structlog.get_logger()
security_scheme = HTTPBearer()


async def get_db() -> AsyncSession:
    """Dependency to get database session."""
    async for session in get_async_session():
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user."""
    try:
        # Verify JWT token
        payload = security.verify_token(credentials.credentials)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise AuthenticationException("Invalid token payload")
        
        # Get user from database
        user = await crud.user.get(db, id=user_id)
        if user is None:
            raise UserNotFoundException(user_id)
        
        if not user.is_active:
            raise InactiveUserException()
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Authentication error", error=str(e))
        raise AuthenticationException("Could not validate credentials")


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to get current active user."""
    if not current_user.is_active:
        raise InactiveUserException()
    return current_user


def require_role(required_roles: list[UserRole]):
    """Dependency factory to require specific roles."""
    
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in required_roles:
            raise AuthorizationException(
                f"Access denied. Required roles: {', '.join(required_roles)}"
            )
        return current_user
    
    return role_checker


# Role-specific dependencies
require_admin = require_role([UserRole.ADMIN])
require_teacher = require_role([UserRole.TEACHER, UserRole.ADMIN])
require_student = require_role([UserRole.STUDENT])
require_guardian = require_role([UserRole.GUARDIAN])

# Multi-role dependencies
require_teacher_or_admin = require_role([UserRole.TEACHER, UserRole.ADMIN])
require_student_or_guardian = require_role([UserRole.STUDENT, UserRole.GUARDIAN])
require_staff = require_role([UserRole.TEACHER, UserRole.ADMIN])


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Dependency to get optional user (for endpoints that work with or without auth)."""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except Exception:
        return None


class PaginationParams:
    """Pagination parameters dependency."""
    
    def __init__(self, page: int = 1, size: int = 10):
        self.page = max(1, page)
        self.size = min(max(1, size), 100)  # Limit max size to 100
        self.skip = (self.page - 1) * self.size
        self.limit = self.size


def get_pagination_params(
    page: int = 1,
    size: int = 10
) -> PaginationParams:
    """Dependency to get pagination parameters."""
    return PaginationParams(page=page, size=size)
