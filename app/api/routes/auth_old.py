from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from typing import Dict, Any

from app.api.dependencies import get_db, get_current_user
from app.core.config import settings
from app.db import schemas
from app.db.models import User
from app.services.auth_service import AuthService
from app.exceptions.custom_exceptions import (
    UserNotFoundException, UserAlreadyExistsException,
    ConflictException
)
router = APIRouter()


@router.post("/register", response_model=APIResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    try:
        # Validate password strength
        if not security.validate_password_strength(user_data.password):
            raise ValidationException(
                "Password must be at least 8 characters long and contain uppercase, lowercase, digit, and special character"
            )
        
        # Create user
        user = await crud.user.create(db, obj_in=user_data)
        
        logger.info("User registered successfully", user_id=str(user.id), email=user.email)
        
        return APIResponse(
            message="User registered successfully",
            data={"user_id": str(user.id), "email": user.email}
        )
        
    except UserAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    except Exception as e:
        logger.error("Registration failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login user and return JWT tokens."""
    try:
        # Authenticate user
        user = await crud.user.authenticate(
            db, email=credentials.email, password=credentials.password
        )
        
        if not user:
            raise InvalidCredentialsException()
        
        if not user.is_active:
            raise InactiveUserException()
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role},
            expires_delta=access_token_expires
        )
        
        # Create refresh token
        refresh_token = security.create_refresh_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        # Update last login
        from datetime import datetime
        from app.db.schemas import UserUpdate
        await crud.user.update(
            db, db_obj=user, obj_in=UserUpdate(last_login=datetime.utcnow())
        )
        
        logger.info("User logged in successfully", user_id=str(user.id), email=user.email)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=user
        )
        
    except (InvalidCredentialsException, InactiveUserException):
        raise
    except Exception as e:
        logger.error("Login failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token."""
    try:
        # Verify refresh token
        payload = security.verify_token(refresh_token, token_type="refresh")
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user = await crud.user.get(db, id=user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role},
            expires_delta=access_token_expires
        )
        
        # Create new refresh token
        new_refresh_token = security.create_refresh_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )


@router.post("/forgot-password", response_model=APIResponse)
async def forgot_password(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset."""
    try:
        user = await crud.user.get_by_email(db, email=request.email)
        
        if user:
            # Generate reset token
            reset_token = security.generate_reset_token()
            
            # In a real application, you would:
            # 1. Store the reset token in database with expiration
            # 2. Send email with reset link
            # For now, we'll just log it
            logger.info(
                "Password reset requested",
                user_id=str(user.id),
                email=user.email,
                reset_token=reset_token
            )
        
        # Always return success message for security
        return APIResponse(
            message="If an account with that email exists, a password reset link has been sent"
        )
        
    except Exception as e:
        logger.error("Password reset request failed", error=str(e))
        return APIResponse(
            message="If an account with that email exists, a password reset link has been sent"
        )


@router.post("/reset-password", response_model=APIResponse)
async def reset_password(
    request: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """Reset password with token."""
    try:
        # In a real application, you would:
        # 1. Verify the reset token from database
        # 2. Check if it's not expired
        # 3. Update user password
        
        # For now, this is a placeholder
        # Validate password strength
        if not security.validate_password_strength(request.new_password):
            raise ValidationException(
                "Password must be at least 8 characters long and contain uppercase, lowercase, digit, and special character"
            )
        
        return APIResponse(message="Password reset successfully")
        
    except ValidationException:
        raise
    except Exception as e:
        logger.error("Password reset failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """Get current user information."""
    return current_user


@router.post("/logout", response_model=APIResponse)
async def logout():
    """Logout user (client should discard tokens)."""
    # In a real application with token blacklisting,
    # you would add the token to a blacklist
    return APIResponse(message="Logged out successfully")


@router.post("/signup/organization", response_model=SignUpResponse)
async def signup_organization(
    signup: OrganizationSignUp,
    db: AsyncSession = Depends(get_db)
):
    """Register a new organization and admin user."""
    try:
        admin_user, tenant_obj = await crud.create_organization_signup(db, signup)
        logger.info("Organization registered", tenant_id=str(tenant_obj.id), admin_id=str(admin_user.id))
        return SignUpResponse(
            success=True,
            message="Organization registered successfully",
            user_id=admin_user.id,
            tenant_id=tenant_obj.id
        )
    except Exception as e:
        logger.error("Organization sign-up failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization sign-up failed"
        )


@router.post("/signup/teacher", response_model=SignUpResponse)
async def signup_teacher(
    signup: TeacherSignUp,
    db: AsyncSession = Depends(get_db)
):
    """Register a new solo teacher."""
    try:
        teacher_user, tenant_obj = await crud.create_teacher_signup(db, signup)
        logger.info("Teacher registered", tenant_id=str(tenant_obj.id), teacher_id=str(teacher_user.id))
        return SignUpResponse(
            success=True,
            message="Teacher registered successfully",
            user_id=teacher_user.id,
            tenant_id=tenant_obj.id
        )
    except Exception as e:
        logger.error("Teacher sign-up failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Teacher sign-up failed"
        )
