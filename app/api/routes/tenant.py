from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.api.dependencies import get_db
from app.db import crud
from app.db.schemas import (
    OrganizationSignUp, TeacherSignUp, SignUpResponse
)

logger = structlog.get_logger()
router = APIRouter()


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
