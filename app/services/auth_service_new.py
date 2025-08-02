"""Main Auth Service: Orchestrates local and Supabase auth services."""
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from uuid import UUID

from app.db import crud, schemas
from app.db.models import User, UserRole, Organization
from app.services.auth_service_local import LocalAuthService
from app.services.auth_service_supabase import SupabaseAuthService
from app.exceptions.custom_exceptions import (
    UserNotFoundException, UserAlreadyExistsException,
    ConflictException
)


class AuthService:
    """Main authentication service that orchestrates local and Supabase auth."""
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession, 
        email: str, 
        password: str
    ) -> Optional[Dict[str, Any]]:
        """Authenticate user and return token data."""
        # Try local authentication first
        user = await LocalAuthService.authenticate_user(db, email, password)
        if not user:
            return None
        
        # Get user roles
        roles = await LocalAuthService.get_user_roles(db, user.id)
        
        # Create token payload
        token_data = LocalAuthService.create_user_token_data(user, roles)
        
        # Create tokens
        access_token = LocalAuthService.create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user,
            "roles": roles
        }
    
    @staticmethod
    async def register_organization(
        db: AsyncSession, 
        signup_data: schemas.OrganizationSignUp
    ) -> Tuple[User, Organization]:
        """Register a new organization with admin user."""
        try:
            # Create organization signup using CRUD
            admin_user, organization = await crud.create_organization_signup(
                db, signup_data
            )
            
            # Optionally sync with Supabase if needed
            # supabase_result = SupabaseAuthService.create_user(
            #     email=signup_data.admin_email,
            #     password=signup_data.admin_password,
            #     user_metadata={
            #         "first_name": signup_data.admin_first_name,
            #         "last_name": signup_data.admin_last_name,
            #         "organization_name": signup_data.organization_name,
            #         "role": "org_owner"
            #     }
            # )
            
            return admin_user, organization
            
        except UserAlreadyExistsException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Organization registration failed: {str(e)}")
    
    @staticmethod
    async def register_solo_teacher(
        db: AsyncSession, 
        signup_data: schemas.TeacherSignUp
    ) -> User:
        """Register a new solo teacher."""
        try:
            # Create teacher signup using CRUD
            teacher_user = await crud.create_teacher_signup(db, signup_data)
            
            # Optionally sync with Supabase if needed
            # supabase_result = SupabaseAuthService.create_user(
            #     email=signup_data.teacher_email,
            #     password=signup_data.teacher_password,
            #     user_metadata={
            #         "first_name": signup_data.teacher_first_name,
            #         "last_name": signup_data.teacher_last_name,
            #         "role": "solo_teacher"
            #     }
            # )
            
            return teacher_user
            
        except UserAlreadyExistsException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Teacher registration failed: {str(e)}")
    
    @staticmethod
    async def get_user_profile(
        db: AsyncSession, 
        user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get complete user profile with roles."""
        user = await crud.user.get(db, id=user_id)
        if not user:
            return None
        
        roles = await crud.user_role.get_user_roles(db, user_id)
        
        return {
            "user": user,
            "roles": roles
        }
    
    @staticmethod
    async def update_user_password(
        db: AsyncSession,
        user_id: UUID,
        current_password: str,
        new_password: str
    ) -> bool:
        """Update user password."""
        user = await crud.user.get(db, id=user_id)
        if not user:
            raise UserNotFoundException("User not found")
        
        # Verify current password
        if not LocalAuthService.verify_password(current_password, user.password_hash):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Hash new password
        hashed_password = LocalAuthService.get_password_hash(new_password)
        
        # Update in database
        user.password_hash = hashed_password
        await db.commit()
        
        return True
    
    @staticmethod
    async def check_user_permission(
        db: AsyncSession,
        user_id: UUID,
        required_role: str,
        organization_id: Optional[UUID] = None
    ) -> bool:
        """Check if user has required permission."""
        return await LocalAuthService.check_user_permission(
            db, user_id, required_role, organization_id
        )
    
    @staticmethod
    async def assign_user_role(
        db: AsyncSession,
        user_id: UUID,
        role: str,
        organization_id: Optional[UUID] = None,
        solo_teacher_id: Optional[UUID] = None
    ) -> UserRole:
        """Assign a role to a user."""
        # Check if role already exists
        existing_role = await crud.user_role.user_has_role(
            db, user_id, role, organization_id
        )
        if existing_role:
            raise ConflictException("User already has this role")
        
        # Create new role
        role_data = {
            "user_id": user_id,
            "role": role,
            "organization_id": organization_id,
            "solo_teacher_id": solo_teacher_id,
            "is_active": True
        }
        
        return await crud.user_role.create(db, obj_in=role_data)
    
    @staticmethod
    async def revoke_user_role(
        db: AsyncSession,
        user_id: UUID,
        role: str,
        organization_id: Optional[UUID] = None
    ) -> bool:
        """Revoke a role from a user."""
        # Find the role
        roles = await crud.user_role.get_user_roles(db, user_id)
        target_role = None
        
        for user_role in roles:
            if (user_role.role == role and 
                user_role.organization_id == organization_id):
                target_role = user_role
                break
        
        if not target_role:
            return False
        
        # Delete the role
        await crud.user_role.delete(db, id=target_role.id)
        return True
    
    @staticmethod
    def get_supabase_config() -> Dict[str, str]:
        """Get Supabase configuration for frontend."""
        return SupabaseAuthService.get_supabase_config()
    
    @staticmethod
    async def handle_supabase_user_sync(
        db: AsyncSession,
        supabase_user_id: str,
        email: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[User]:
        """Sync user from Supabase to local database."""
        return await SupabaseAuthService.sync_user_from_supabase(
            db, supabase_user_id, email, metadata
        )
