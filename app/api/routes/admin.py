from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import structlog

from app.api.dependencies import get_db, require_admin, get_pagination_params, PaginationParams
from app.db import crud
from app.db.crud import get_user_statistics
from app.db.schemas import (
    UserCreate, UserUpdate, UserResponse, ClassCreate, ClassUpdate, ClassResponse,
    APIResponse, PaginatedResponse
)
from app.exceptions.custom_exceptions import UserNotFoundException, ClassNotFoundException

logger = structlog.get_logger()
router = APIRouter()


@router.get("/users", response_model=PaginatedResponse)
async def get_users(
    pagination: PaginationParams = Depends(get_pagination_params),
    role: str = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Get all users with pagination and optional role filter."""
    try:

        # Debug logging
        logger.info(f"Pagination object: {pagination}")
        logger.info(f"Pagination page: {pagination.page}")
        logger.info(f"Pagination size: {pagination.size}")
        logger.info(f"Pagination skip: {getattr(pagination, 'skip', 'NOT FOUND')}")


        # Get users
        users = await crud.user.get_multi(
            db, 
            skip=pagination.skip, 
            limit=pagination.limit,
            role=role
        )
        
        # Get total count
        total = await crud.user.count(db, role=role)
        
        return PaginatedResponse(
            items=[UserResponse.model_validate(user) for user in users],
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
        
    except Exception as e:
        logger.error("Failed to get users", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Create a new user (admin only)."""
    try:
        user = await crud.user.create(db, obj_in=user_data)
        logger.info("User created by admin", user_id=str(user.id), created_by=str(current_user.id))
        return UserResponse.model_validate(user)  
        
    except Exception as e:
        logger.error("Failed to create user", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Get user by ID."""
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise UserNotFoundException(str(user_id))
    return UserResponse.model_validate(user)  


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Update user."""
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise UserNotFoundException(str(user_id))
    
    updated_user = await crud.user.update(db, db_obj=user, obj_in=user_update)
    logger.info("User updated by admin", user_id=str(user_id), updated_by=str(current_user.id))
    return UserResponse.model_validate(updated_user)  


@router.delete("/users/{user_id}", response_model=APIResponse)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Delete user (soft delete by deactivating)."""
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise UserNotFoundException(str(user_id))
    
    # Soft delete by deactivating
    await crud.user.update(db, db_obj=user, obj_in={"is_active": False})
    logger.info("User deactivated by admin", user_id=str(user_id), deactivated_by=str(current_user.id))
    
    return APIResponse(message="User deactivated successfully")


@router.get("/classes", response_model=List[ClassResponse])
async def get_classes(
    pagination: PaginationParams = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Get all classes."""
    try:
        classes = await crud.class_.get_multi(
            db, 
            skip=pagination.skip, 
            limit=pagination.limit,
            is_active=True
        )
        return classes
        
    except Exception as e:
        logger.error("Failed to get classes", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve classes"
        )


@router.post("/classes", response_model=ClassResponse)
async def create_class(
    class_data: ClassCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Create a new class."""
    try:
        class_obj = await crud.class_.create(db, obj_in=class_data)
        logger.info("Class created by admin", class_id=str(class_obj.id), created_by=str(current_user.id))
        return class_obj
        
    except Exception as e:
        logger.error("Failed to create class", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create class"
        )


@router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Get admin dashboard statistics."""
    try:
        # Use your existing CRUD function
        user_stats = await get_user_statistics(db)
        
        # Transform to match what your frontend expects
        return {
            "total_users": user_stats["total_users"],
            "total_students": user_stats["role_distribution"].get("student", 0),
            "total_teachers": user_stats["role_distribution"].get("teacher", 0),
            "total_guardians": user_stats["role_distribution"].get("guardian", 0),
            "total_classes": 0,  # Add when you implement class stats
            "active_teachers": user_stats["role_distribution"].get("teacher", 0)
        }
    except Exception as e:
        logger.error("Failed to get dashboard stats", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard statistics"
        )
