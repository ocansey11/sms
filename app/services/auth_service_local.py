"""Local Auth Service: Handles backend-specific authentication tasks."""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import crud
from app.db.models import User, UserRole
from app.core.security import security
from app.core.config import settings

class LocalAuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password."""
        return security.verify_password(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a plain password."""
        return security.get_password_hash(password)

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = data.copy()
        to_encode.update({"exp": expire})
        return security.create_access_token(to_encode)

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = await crud.user.get_by_email(db, email=email)
        if not user:
            return None
        if not LocalAuthService.verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    async def get_user_roles(db: AsyncSession, user_id: UUID) -> list[UserRole]:
        """Get all roles for a user."""
        return await crud.user_role.get_user_roles(db, user_id=user_id)

    @staticmethod
    async def user_has_role(
        db: AsyncSession, 
        user_id: UUID, 
        role: str, 
        organization_id: Optional[UUID] = None
    ) -> bool:
        """Check if user has specific role."""
        return await crud.user_role.user_has_role(db, user_id=user_id, role=role, organization_id=organization_id)

    @staticmethod
    def create_user_token_data(user: User, roles: list[UserRole]) -> Dict[str, Any]:
        """Create token data for JWT."""
        return {
            "sub": str(user.id),
            "email": user.email,
            "roles": [
                {
                    "role": role.role,
                    "organization_id": str(role.organization_id) if role.organization_id else None,
                    "solo_teacher_id": str(role.solo_teacher_id) if role.solo_teacher_id else None
                }
                for role in roles
            ]
        }
