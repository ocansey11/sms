from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
import structlog

from app.db import crud, schemas
from app.core.security import SecurityManager
from app.exceptions.custom_exceptions import SMSException

logger = structlog.get_logger()

class AuthService:
    """Authentication and authorization service"""
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[schemas.UserResponse]:
        """Authenticate user with email and password"""
        try:
            user = await crud.get_user_by_email(db, email=email)
            if not user or not SecurityManager.verify_password(password, user.password_hash):
                return None
            return user
        except Exception as e:
            logger.error("Authentication failed", error=str(e))
            return None
    
    @staticmethod
    async def register_user(db: AsyncSession, user_create: schemas.UserCreate) -> schemas.UserResponse:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = await crud.get_user_by_email(db, email=user_create.email)
            if existing_user:
                raise SMSException("User already exists", "USER_EXISTS")
            
            # Hash password
            user_create.password = SecurityManager.get_password_hash(user_create.password)
            
            # Create user
            user = await crud.create_user(db, user=user_create)
            logger.info("User registered successfully", user_id=user.id, email=user.email)
            return user
        except SMSException:
            raise
        except Exception as e:
            logger.error("User registration failed", error=str(e))
            raise SMSException("Registration failed", "REGISTRATION_ERROR")
    
    @staticmethod
    async def update_user_password(
        db: AsyncSession, 
        user_id: int, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """Update user password"""
        try:
            user = await crud.get_user_by_id(db, user_id=user_id)
            if not user:
                raise SMSException("User not found", "USER_NOT_FOUND")
            
            # Verify current password
            if not SecurityManager.verify_password(current_password, user.password_hash):
                raise SMSException("Current password is incorrect", "INVALID_PASSWORD")
            
            # Update password
            hashed_new_password = SecurityManager.get_password_hash(new_password)
            await crud.update_user_password(db, user_id=user_id, hashed_password=hashed_new_password)
            
            logger.info("Password updated successfully", user_id=user_id)
            return True
        except SMSException:
            raise
        except Exception as e:
            logger.error("Password update failed", error=str(e))
            raise SMSException("Password update failed", "PASSWORD_UPDATE_ERROR")
    
    @staticmethod
    async def deactivate_user(db: AsyncSession, user_id: int) -> bool:
        """Deactivate a user account"""
        try:
            user = await crud.get_user_by_id(db, user_id=user_id)
            if not user:
                raise SMSException("User not found", "USER_NOT_FOUND")
            
            await crud.deactivate_user(db, user_id=user_id)
            logger.info("User deactivated", user_id=user_id)
            return True
        except SMSException:
            raise
        except Exception as e:
            logger.error("User deactivation failed", error=str(e))
            raise SMSException("User deactivation failed", "DEACTIVATION_ERROR")

class UserService:
    """User management service"""
    
    @staticmethod
    async def get_users_by_role(
        db: AsyncSession, 
        role: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[schemas.UserResponse]:
        """Get users by role with pagination"""
        try:
            users = await crud.get_users_by_role(db, role=role, skip=skip, limit=limit)
            return users
        except Exception as e:
            logger.error("Failed to get users by role", error=str(e))
            raise SMSException("Failed to retrieve users", "USERS_FETCH_ERROR")
    
    @staticmethod
    async def update_user_profile(
        db: AsyncSession, 
        user_id: int, 
        profile_update: schemas.UserUpdate
    ) -> schemas.UserResponse:
        """Update user profile"""
        try:
            user = await crud.get_user_by_id(db, user_id=user_id)
            if not user:
                raise SMSException("User not found", "USER_NOT_FOUND")
            
            updated_user = await crud.update_user(db, user_id=user_id, user_update=profile_update)
            logger.info("User profile updated", user_id=user_id)
            return updated_user
        except SMSException:
            raise
        except Exception as e:
            logger.error("Profile update failed", error=str(e))
            raise SMSException("Profile update failed", "PROFILE_UPDATE_ERROR")
    
    @staticmethod
    async def get_user_statistics(db: AsyncSession) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            stats = await crud.get_user_statistics(db)
            return stats
        except Exception as e:
            logger.error("Failed to get user statistics", error=str(e))
            raise SMSException("Failed to retrieve statistics", "STATS_ERROR")

class NotificationService:
    """Notification service for sending emails, SMS, etc."""
    
    @staticmethod
    async def send_welcome_email(user: schemas.UserResponse) -> bool:
        """Send welcome email to new user"""
        try:
            # This would integrate with email service (SendGrid, AWS SES, etc.)
            logger.info("Welcome email sent", user_id=user.id, email=user.email)
            return True
        except Exception as e:
            logger.error("Failed to send welcome email", error=str(e))
            return False
    
    @staticmethod
    async def send_password_reset_email(user: schemas.UserResponse, reset_token: str) -> bool:
        """Send password reset email"""
        try:
            # This would integrate with email service
            logger.info("Password reset email sent", user_id=user.id, email=user.email)
            return True
        except Exception as e:
            logger.error("Failed to send password reset email", error=str(e))
            return False
    
    @staticmethod
    async def send_attendance_notification(
        guardian: schemas.UserResponse, 
        student: schemas.UserResponse, 
        attendance_status: str
    ) -> bool:
        """Send attendance notification to guardian"""
        try:
            # This would integrate with email/SMS service
            logger.info(
                "Attendance notification sent", 
                guardian_id=guardian.id, 
                student_id=student.id, 
                status=attendance_status
            )
            return True
        except Exception as e:
            logger.error("Failed to send attendance notification", error=str(e))
            return False
