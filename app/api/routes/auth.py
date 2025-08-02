"""Auth API routes using updated service layer."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.api.dependencies import get_db, get_current_user
from app.db import schemas
from app.db.models import User
from app.services.auth_service import AuthService
from app.exceptions.custom_exceptions import (
    UserNotFoundException, UserAlreadyExistsException,
    ConflictException
)

router = APIRouter()


@router.post("/login", response_model=Dict[str, Any])
async def login(
    credentials: schemas.LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login user and return access token with user data."""
    try:
        result = await AuthService.authenticate_user(
            db, credentials.email, credentials.password
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        return {
            "message": "Login successful",
            "access_token": result["access_token"],
            "token_type": result["token_type"],
            "user": {
                "id": str(result["user"].id),
                "email": result["user"].email,
                "first_name": result["user"].first_name,
                "last_name": result["user"].last_name,
                "is_active": result["user"].is_active
            },
            "roles": [
                {
                    "role": role.role,
                    "organization_id": str(role.organization_id) if role.organization_id else None,
                    "solo_teacher_id": str(role.solo_teacher_id) if role.solo_teacher_id else None
                }
                for role in result["roles"]
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/signup/organization", response_model=Dict[str, Any])
async def signup_organization(
    signup: schemas.OrganizationSignUp,
    db: AsyncSession = Depends(get_db)
):
    """Register a new organization with admin user."""
    try:
        admin_user, organization = await AuthService.register_organization(db, signup)
        
        return {
            "success": True,
            "message": "Organization registered successfully",
            "user": {
                "id": str(admin_user.id),
                "email": admin_user.email,
                "first_name": admin_user.first_name,
                "last_name": admin_user.last_name
            },
            "organization": {
                "id": str(organization.id),
                "name": organization.name
            }
        }
        
    except UserAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Organization registration failed: {str(e)}"
        )


@router.post("/signup/teacher", response_model=Dict[str, Any])
async def signup_teacher(
    signup: schemas.TeacherSignUp,
    db: AsyncSession = Depends(get_db)
):
    """Register a new solo teacher."""
    try:
        teacher_user = await AuthService.register_solo_teacher(db, signup)
        
        return {
            "success": True,
            "message": "Solo teacher registered successfully",
            "user": {
                "id": str(teacher_user.id),
                "email": teacher_user.email,
                "first_name": teacher_user.first_name,
                "last_name": teacher_user.last_name
            }
        }
        
    except UserAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Teacher registration failed: {str(e)}"
        )


@router.get("/me", response_model=Dict[str, Any])
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user profile with roles."""
    try:
        profile = await AuthService.get_user_profile(db, current_user.id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return {
            "user": {
                "id": str(profile["user"].id),
                "email": profile["user"].email,
                "first_name": profile["user"].first_name,
                "last_name": profile["user"].last_name,
                "is_active": profile["user"].is_active,
                "created_at": profile["user"].created_at.isoformat() if profile["user"].created_at else None
            },
            "roles": [
                {
                    "role": role.role,
                    "organization_id": str(role.organization_id) if role.organization_id else None,
                    "solo_teacher_id": str(role.solo_teacher_id) if role.solo_teacher_id else None,
                    "is_active": role.is_active
                }
                for role in profile["roles"]
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )


@router.put("/change-password", response_model=Dict[str, str])
async def change_password(
    password_data: schemas.PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password."""
    try:
        success = await AuthService.update_user_password(
            db, 
            current_user.id, 
            password_data.current_password, 
            password_data.new_password
        )
        
        if success:
            return {"message": "Password updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password update failed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password update failed: {str(e)}"
        )


@router.post("/assign-role", response_model=Dict[str, str])
async def assign_role(
    role_data: schemas.UserRoleAssignment,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Assign a role to a user (admin only)."""
    try:
        # Check if current user has permission to assign roles
        has_permission = await AuthService.check_user_permission(
            db, current_user.id, "org_owner", role_data.organization_id
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to assign roles"
            )
        
        user_role = await AuthService.assign_user_role(
            db,
            role_data.user_id,
            role_data.role,
            role_data.organization_id,
            role_data.solo_teacher_id
        )
        
        return {"message": f"Role '{role_data.role}' assigned successfully"}
        
    except ConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Role assignment failed: {str(e)}"
        )


@router.delete("/revoke-role", response_model=Dict[str, str])
async def revoke_role(
    role_data: schemas.UserRoleRevocation,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Revoke a role from a user (admin only)."""
    try:
        # Check if current user has permission to revoke roles
        has_permission = await AuthService.check_user_permission(
            db, current_user.id, "org_owner", role_data.organization_id
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to revoke roles"
            )
        
        success = await AuthService.revoke_user_role(
            db,
            role_data.user_id,
            role_data.role,
            role_data.organization_id
        )
        
        if success:
            return {"message": f"Role '{role_data.role}' revoked successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role assignment not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Role revocation failed: {str(e)}"
        )


@router.get("/supabase-config", response_model=Dict[str, str])
async def get_supabase_config():
    """Get Supabase configuration for frontend."""
    return AuthService.get_supabase_config()


@router.post("/supabase-sync", response_model=Dict[str, str])
async def sync_supabase_user(
    sync_data: schemas.SupabaseUserSync,
    db: AsyncSession = Depends(get_db)
):
    """Sync user from Supabase to local database."""
    try:
        user = await AuthService.handle_supabase_user_sync(
            db,
            sync_data.supabase_user_id,
            sync_data.email,
            sync_data.metadata
        )
        
        if user:
            return {"message": "User synced successfully", "user_id": str(user.id)}
        else:
            return {"message": "User sync failed"}
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User sync failed: {str(e)}"
        )
