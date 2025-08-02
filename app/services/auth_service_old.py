from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from uuid import UUID

from app.db import crud, schemas
from app.db.models import User, UserRole
from app.services.auth_service_local import LocalAuthService
from app.services.auth_service_supabase import SupabaseAuthService
from app.exceptions.custom_exceptions import (
    UserNotFoundException, UserAlreadyExistsException, 
    SMSException
)


class AuthService:
    """Authentication and authorization service - orchestrates local and Supabase auth"""
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password using local auth"""
        try:
            return await LocalAuthService.authenticate_user(db, email, password)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")
    
    @staticmethod
    async def register_organization(
        db: AsyncSession, 
        signup_data: schemas.OrganizationSignUp
    ) -> Dict[str, Any]:
        """Register a new organization with admin user"""
        try:
            # Use the CRUD function we created
            admin_user, organization = await crud.create_organization_signup(db, signup_data)
            
            # Get user roles for token creation
            roles = await LocalAuthService.get_user_roles(db, admin_user.id)
            
            # Create access token
            token_data = LocalAuthService.create_user_token_data(admin_user, roles)
            access_token = LocalAuthService.create_access_token(token_data)
            
            return {
                "user": admin_user,
                "organization": organization,
                "access_token": access_token,
                "token_type": "bearer"
            }
        except UserAlreadyExistsException:
            raise HTTPException(status_code=400, detail="User already exists")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Organization registration failed: {str(e)}")
    
    @staticmethod
    async def register_solo_teacher(
        db: AsyncSession, 
        signup_data: schemas.TeacherSignUp
    ) -> Dict[str, Any]:
        """Register a new solo teacher"""
        try:
            # Use the CRUD function we created
            teacher_user = await crud.create_teacher_signup(db, signup_data)
            
            # Get user roles for token creation
            roles = await LocalAuthService.get_user_roles(db, teacher_user.id)
            
            # Create access token
            token_data = LocalAuthService.create_user_token_data(teacher_user, roles)
            access_token = LocalAuthService.create_access_token(token_data)
            
            return {
                "user": teacher_user,
                "access_token": access_token,
                "token_type": "bearer"
            }
        except UserAlreadyExistsException:
            raise HTTPException(status_code=400, detail="User already exists")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Solo teacher registration failed: {str(e)}")
    
    @staticmethod
    async def login_user(
        db: AsyncSession, 
        email: str, 
        password: str
    ) -> Dict[str, Any]:
        """Login user and return access token"""
        # Authenticate user
        user = await AuthService.authenticate_user(db, email, password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not user.is_active:
            raise HTTPException(status_code=400, detail="User account is deactivated")
        
        # Get user roles
        roles = await LocalAuthService.get_user_roles(db, user.id)
        
        # Create access token
        token_data = LocalAuthService.create_user_token_data(user, roles)
        access_token = LocalAuthService.create_access_token(token_data)
        
        return {
            "user": user,
            "access_token": access_token,
            "token_type": "bearer",
            "roles": roles
        }
    
    @staticmethod
    async def change_password(
        db: AsyncSession, 
        user_id: UUID, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """Change user password"""
        try:
            user = await crud.user.get(db, id=user_id)
            if not user:
                raise UserNotFoundException("User not found")
            
            # Verify current password
            if not LocalAuthService.verify_password(current_password, user.password_hash):
                raise HTTPException(status_code=400, detail="Current password is incorrect")
            
            # Hash new password and update
            hashed_new_password = LocalAuthService.get_password_hash(new_password)
            await crud.update_user_password(db, user_id=user_id, hashed_password=hashed_new_password)
            
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Password update failed: {str(e)}")
    
    @staticmethod
    async def deactivate_user(db: AsyncSession, user_id: UUID) -> bool:
        """Deactivate user account"""
        try:
            result = await crud.deactivate_user(db, user_id=user_id)
            if not result:
                raise UserNotFoundException("User not found")
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"User deactivation failed: {str(e)}")
    
    @staticmethod
    async def assign_user_role(
        db: AsyncSession,
        user_id: UUID,
        role: str,
        organization_id: Optional[UUID] = None,
        solo_teacher_id: Optional[UUID] = None
    ) -> UserRole:
        """Assign a role to a user"""
        try:
            # Check if role already exists
            has_role = await LocalAuthService.user_has_role(db, user_id, role, organization_id)
            if has_role:
                raise HTTPException(status_code=400, detail="User already has this role")
            
            # Create role assignment
            role_data = {
                "user_id": user_id,
                "role": role,
                "organization_id": organization_id,
                "solo_teacher_id": solo_teacher_id,
                "is_active": True
            }
            
            return await crud.user_role.create(db, obj_in=role_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Role assignment failed: {str(e)}")
    
    @staticmethod
    async def remove_user_role(
        db: AsyncSession,
        user_id: UUID,
        role: str,
        organization_id: Optional[UUID] = None
    ) -> bool:
        """Remove a role from a user"""
        try:
            # Get the role to remove
            roles = await crud.user_role.get_user_roles(db, user_id)
            role_to_remove = None
            
            for user_role in roles:
                if (user_role.role == role and 
                    user_role.organization_id == organization_id):
                    role_to_remove = user_role
                    break
            
            if role_to_remove:
                await crud.user_role.delete(db, id=role_to_remove.id)
                return True
            
            return False
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Role removal failed: {str(e)}")
    
    @staticmethod
    async def get_user_permissions(db: AsyncSession, user_id: UUID) -> Dict[str, Any]:
        """Get user permissions based on roles"""
        try:
            roles = await LocalAuthService.get_user_roles(db, user_id)
            
            permissions = {
                "roles": [],
                "organizations": [],
                "is_solo_teacher": False,
                "can_create_courses": False,
                "can_manage_users": False
            }
            
            for role in roles:
                role_info = {
                    "role": role.role,
                    "organization_id": role.organization_id,
                    "solo_teacher_id": role.solo_teacher_id
                }
                permissions["roles"].append(role_info)
                
                # Add organization to list if not already there
                if role.organization_id and role.organization_id not in permissions["organizations"]:
                    permissions["organizations"].append(role.organization_id)
                
                # Set permissions based on role
                if role.role in ["org_owner", "org_admin"]:
                    permissions["can_create_courses"] = True
                    permissions["can_manage_users"] = True
                elif role.role == "solo_teacher":
                    permissions["is_solo_teacher"] = True
                    permissions["can_create_courses"] = True
            
            return permissions
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get user permissions: {str(e)}")
    
    @staticmethod
    async def update_user_profile(
        db: AsyncSession,
        user_id: UUID,
        profile_update: schemas.UserUpdate
    ) -> User:
        """Update user profile"""
        try:
            user = await crud.user.get(db, id=user_id)
            if not user:
                raise UserNotFoundException("User not found")
            
            updated_user = await crud.user.update(db, db_obj=user, obj_in=profile_update)
            return updated_user
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Profile update failed: {str(e)}")
    
    @staticmethod
    async def get_supabase_config() -> Dict[str, str]:
        """Get Supabase configuration for frontend"""
        return SupabaseAuthService.get_supabase_config()
    
    @staticmethod
    async def handle_supabase_user_sync(
        db: AsyncSession,
        supabase_user_id: str,
        email: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[User]:
        """Sync user from Supabase to local database"""
        return await SupabaseAuthService.sync_user_from_supabase(
            db, supabase_user_id, email, metadata
        )
                admin_email=signup_data.admin_email,
                admin_first_name=signup_data.admin_first_name,
                admin_last_name=signup_data.admin_last_name,
                admin_password_hash=hashed_password
            )
            
            logger.info(
                "Organization registered successfully", 
                organization_id=result["organization_id"],
                admin_id=result["user_id"],
                email=signup_data.admin_email
            )
            
            return schemas.SignUpResponse(
                success=True,
                message="Organization registered successfully",
                user_id=result["user_id"],
                organization_id=result["organization_id"]
            )
        except SMSException:
            raise
        except Exception as e:
            logger.error("Organization registration failed", error=str(e))
            raise SMSException("Registration failed", "REGISTRATION_ERROR")
    
    @staticmethod
    async def register_solo_teacher(
        db: AsyncSession, 
        signup_data: schemas.TeacherSignUp
    ) -> schemas.SignUpResponse:
        """Register a new solo teacher"""
        try:
            # Check if user already exists
            existing_user = await crud.get_user_by_email(db, email=signup_data.teacher_email)
            if existing_user:
                raise SMSException("User already exists", "USER_EXISTS")
            
            # Hash password
            hashed_password = SecurityManager.get_password_hash(signup_data.teacher_password)
            
            # Create solo teacher user
            user_id = await crud.create_solo_teacher(
                db,
                email=signup_data.teacher_email,
                first_name=signup_data.teacher_first_name,
                last_name=signup_data.teacher_last_name,
                password_hash=hashed_password
            )
            
            logger.info(
                "Solo teacher registered successfully", 
                user_id=user_id,
                email=signup_data.teacher_email
            )
            
            return schemas.SignUpResponse(
                success=True,
                message="Solo teacher registered successfully",
                user_id=user_id
            )
        except SMSException:
            raise
        except Exception as e:
            logger.error("Solo teacher registration failed", error=str(e))
            raise SMSException("Registration failed", "REGISTRATION_ERROR")
    
    @staticmethod
    async def update_user_password(
        db: AsyncSession, 
        user_id: UUID, 
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
    async def deactivate_user(db: AsyncSession, user_id: UUID) -> bool:
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
    
    @staticmethod
    async def assign_user_role(
        db: AsyncSession,
        user_id: UUID,
        role: str,
        organization_id: Optional[UUID] = None,
        solo_teacher_id: Optional[UUID] = None
    ) -> schemas.UserRoleResponse:
        """Assign a role to a user"""
        try:
            # Verify user exists
            user = await crud.get_user_by_id(db, user_id=user_id)
            if not user:
                raise SMSException("User not found", "USER_NOT_FOUND")
            
            # Verify role exists
            role_obj = await crud.get_role(db, role=role)
            if not role_obj:
                raise SMSException("Invalid role", "INVALID_ROLE")
            
            # Check if role assignment already exists
            existing_role = await crud.get_user_role(
                db, 
                user_id=user_id, 
                role=role, 
                organization_id=organization_id,
                solo_teacher_id=solo_teacher_id
            )
            if existing_role:
                raise SMSException("Role already assigned", "ROLE_EXISTS")
            
            # Create role assignment
            user_role = await crud.create_user_role(
                db,
                user_id=user_id,
                role=role,
                organization_id=organization_id,
                solo_teacher_id=solo_teacher_id
            )
            
            logger.info(
                "Role assigned successfully", 
                user_id=user_id, 
                role=role,
                organization_id=organization_id,
                solo_teacher_id=solo_teacher_id
            )
            return user_role
        except SMSException:
            raise
        except Exception as e:
            logger.error("Role assignment failed", error=str(e))
            raise SMSException("Role assignment failed", "ROLE_ASSIGNMENT_ERROR")
    
    @staticmethod
    async def remove_user_role(
        db: AsyncSession,
        user_id: UUID,
        role: str,
        organization_id: Optional[UUID] = None,
        solo_teacher_id: Optional[UUID] = None
    ) -> bool:
        """Remove a role from a user"""
        try:
            result = await crud.delete_user_role(
                db,
                user_id=user_id,
                role=role,
                organization_id=organization_id,
                solo_teacher_id=solo_teacher_id
            )
            
            if result:
                logger.info(
                    "Role removed successfully", 
                    user_id=user_id, 
                    role=role,
                    organization_id=organization_id,
                    solo_teacher_id=solo_teacher_id
                )
            else:
                raise SMSException("Role assignment not found", "ROLE_NOT_FOUND")
            
            return True
        except SMSException:
            raise
        except Exception as e:
            logger.error("Role removal failed", error=str(e))
            raise SMSException("Role removal failed", "ROLE_REMOVAL_ERROR")


class UserService:
    """User management service"""
    
    @staticmethod
    async def get_users_by_role(
        db: AsyncSession, 
        role: str,
        organization_id: Optional[UUID] = None,
        solo_teacher_id: Optional[UUID] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[schemas.UserResponse]:
        """Get users by role with pagination"""
        try:
            users = await crud.get_users_by_role(
                db, 
                role=role,
                organization_id=organization_id,
                solo_teacher_id=solo_teacher_id,
                skip=skip, 
                limit=limit
            )
            return users
        except Exception as e:
            logger.error("Failed to get users by role", error=str(e))
            raise SMSException("Failed to retrieve users", "USERS_FETCH_ERROR")
    
    @staticmethod
    async def update_user_profile(
        db: AsyncSession, 
        user_id: UUID, 
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
    async def get_user_roles(db: AsyncSession, user_id: UUID) -> List[schemas.UserRoleResponse]:
        """Get all roles for a user"""
        try:
            roles = await crud.get_user_roles(db, user_id=user_id)
            return roles
        except Exception as e:
            logger.error("Failed to get user roles", error=str(e))
            raise SMSException("Failed to retrieve user roles", "USER_ROLES_ERROR")
    
    @staticmethod
    async def has_role(
        db: AsyncSession, 
        user_id: UUID, 
        role: str,
        organization_id: Optional[UUID] = None,
        solo_teacher_id: Optional[UUID] = None
    ) -> bool:
        """Check if user has specific role"""
        try:
            user_role = await crud.get_user_role(
                db,
                user_id=user_id,
                role=role,
                organization_id=organization_id,
                solo_teacher_id=solo_teacher_id
            )
            return user_role is not None
        except Exception as e:
            logger.error("Failed to check user role", error=str(e))
            return False
    
    @staticmethod
    async def get_organization_users(
        db: AsyncSession,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[schemas.UserResponse]:
        """Get all users in an organization"""
        try:
            users = await crud.get_organization_users(
                db,
                organization_id=organization_id,
                skip=skip,
                limit=limit
            )
            return users
        except Exception as e:
            logger.error("Failed to get organization users", error=str(e))
            raise SMSException("Failed to retrieve organization users", "ORG_USERS_ERROR")
    
    @staticmethod
    async def get_user_statistics(
        db: AsyncSession,
        organization_id: Optional[UUID] = None,
        solo_teacher_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            stats = await crud.get_user_statistics(
                db,
                organization_id=organization_id,
                solo_teacher_id=solo_teacher_id
            )
            return stats
        except Exception as e:
            logger.error("Failed to get user statistics", error=str(e))
            raise SMSException("Failed to retrieve statistics", "STATS_ERROR")


class GuardianService:
    """Guardian-child relationship service"""
    
    @staticmethod
    async def create_guardian_child_relationship(
        db: AsyncSession,
        relationship_data: schemas.GuardianChildCreate
    ) -> schemas.GuardianChildResponse:
        """Create guardian-child relationship"""
        try:
            # Verify guardian exists and has guardian role
            guardian = await crud.get_user_by_id(db, user_id=relationship_data.guardian_id)
            if not guardian:
                raise SMSException("Guardian not found", "GUARDIAN_NOT_FOUND")
            
            # Verify student exists and has student role
            student = await crud.get_user_by_id(db, user_id=relationship_data.student_id)
            if not student:
                raise SMSException("Student not found", "STUDENT_NOT_FOUND")
            
            # Check if relationship already exists
            existing = await crud.get_guardian_child_relationship(
                db,
                guardian_id=relationship_data.guardian_id,
                student_id=relationship_data.student_id
            )
            if existing:
                raise SMSException("Relationship already exists", "RELATIONSHIP_EXISTS")
            
            # Create relationship
            relationship = await crud.create_guardian_child_relationship(db, relationship_data)
            
            logger.info(
                "Guardian-child relationship created",
                guardian_id=relationship_data.guardian_id,
                student_id=relationship_data.student_id
            )
            return relationship
        except SMSException:
            raise
        except Exception as e:
            logger.error("Failed to create guardian-child relationship", error=str(e))
            raise SMSException("Relationship creation failed", "RELATIONSHIP_ERROR")
    
    @staticmethod
    async def get_guardian_children(
        db: AsyncSession,
        guardian_id: UUID
    ) -> List[schemas.GuardianChildResponse]:
        """Get all children for a guardian"""
        try:
            children = await crud.get_guardian_children(db, guardian_id=guardian_id)
            return children
        except Exception as e:
            logger.error("Failed to get guardian children", error=str(e))
            raise SMSException("Failed to retrieve children", "CHILDREN_FETCH_ERROR")
    
    @staticmethod
    async def get_student_guardians(
        db: AsyncSession,
        student_id: UUID
    ) -> List[schemas.GuardianChildResponse]:
        """Get all guardians for a student"""
        try:
            guardians = await crud.get_student_guardians(db, student_id=student_id)
            return guardians
        except Exception as e:
            logger.error("Failed to get student guardians", error=str(e))
            raise SMSException("Failed to retrieve guardians", "GUARDIANS_FETCH_ERROR")
    
    @staticmethod
    async def update_guardian_child_relationship(
        db: AsyncSession,
        guardian_id: UUID,
        student_id: UUID,
        update_data: schemas.GuardianChildUpdate
    ) -> schemas.GuardianChildResponse:
        """Update guardian-child relationship"""
        try:
            relationship = await crud.update_guardian_child_relationship(
                db,
                guardian_id=guardian_id,
                student_id=student_id,
                update_data=update_data
            )
            
            if not relationship:
                raise SMSException("Relationship not found", "RELATIONSHIP_NOT_FOUND")
            
            logger.info(
                "Guardian-child relationship updated",
                guardian_id=guardian_id,
                student_id=student_id
            )
            return relationship
        except SMSException:
            raise
        except Exception as e:
            logger.error("Failed to update guardian-child relationship", error=str(e))
            raise SMSException("Relationship update failed", "RELATIONSHIP_UPDATE_ERROR")


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
    async def send_guardian_invitation(
        guardian: schemas.UserResponse,
        student: schemas.UserResponse,
        invitation_token: str
    ) -> bool:
        """Send guardian invitation email"""
        try:
            # This would integrate with email/SMS service
            logger.info(
                "Guardian invitation sent",
                guardian_id=guardian.id,
                student_id=student.id,
                guardian_email=guardian.email
            )
            return True
        except Exception as e:
            logger.error("Failed to send guardian invitation", error=str(e))
            return False
    
    @staticmethod
    async def send_role_assignment_notification(
        user: schemas.UserResponse,
        role: str,
        organization_name: Optional[str] = None
    ) -> bool:
        """Send role assignment notification"""
        try:
            logger.info(
                "Role assignment notification sent",
                user_id=user.id,
                role=role,
                organization=organization_name
            )
            return True
        except Exception as e:
            logger.error("Failed to send role assignment notification", error=str(e))
            return False