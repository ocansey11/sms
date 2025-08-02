"""Course API routes using updated service layer."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from uuid import UUID

from app.api.dependencies import get_db, get_current_user
from app.db import schemas
from app.db.models import User
from app.services.course_service import CourseService
from app.exceptions.custom_exceptions import (
    ConflictException
)

router = APIRouter()


@router.post("/", response_model=Dict[str, Any])
async def create_course(
    course_data: schemas.CourseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new course."""
    try:
        course = await CourseService.create_course(db, course_data, current_user.id)
        
        return {
            "message": "Course created successfully",
            "course": {
                "id": str(course.id),
                "title": course.title,
                "description": course.description,
                "organization_id": str(course.organization_id) if course.organization_id else None,
                "solo_teacher_id": str(course.solo_teacher_id) if course.solo_teacher_id else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Course creation failed: {str(e)}"
        )


@router.get("/{course_id}", response_model=Dict[str, Any])
async def get_course(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get course by ID."""
    try:
        course = await CourseService.get_course_by_id(db, course_id)
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        return {
            "course": {
                "id": str(course.id),
                "title": course.title,
                "description": course.description,
                "organization_id": str(course.organization_id) if course.organization_id else None,
                "solo_teacher_id": str(course.solo_teacher_id) if course.solo_teacher_id else None,
                "created_at": course.created_at.isoformat() if course.created_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get course: {str(e)}"
        )


@router.get("/", response_model=Dict[str, Any])
async def get_courses(
    skip: int = 0,
    limit: int = 100,
    organization_id: UUID = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get courses based on user permissions."""
    try:
        if organization_id:
            courses = await CourseService.get_organization_courses(
                db, organization_id, skip, limit
            )
        else:
            # Get courses for solo teacher
            courses = await CourseService.get_teacher_courses(
                db, current_user.id, skip, limit
            )
        
        return {
            "courses": [
                {
                    "id": str(course.id),
                    "title": course.title,
                    "description": course.description,
                    "organization_id": str(course.organization_id) if course.organization_id else None,
                    "solo_teacher_id": str(course.solo_teacher_id) if course.solo_teacher_id else None
                }
                for course in courses
            ],
            "total": len(courses)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get courses: {str(e)}"
        )


@router.post("/{course_id}/enroll", response_model=Dict[str, str])
async def enroll_student(
    course_id: UUID,
    enrollment_data: schemas.StudentEnrollmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Enroll a student in a course."""
    try:
        enrollment = await CourseService.enroll_student(
            db, course_id, enrollment_data.student_id, current_user.id
        )
        
        return {"message": "Student enrolled successfully"}
        
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
            detail=f"Enrollment failed: {str(e)}"
        )


@router.get("/{course_id}/students", response_model=Dict[str, Any])
async def get_course_students(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all students enrolled in a course."""
    try:
        students = await CourseService.get_course_students(db, course_id)
        
        return {
            "students": [
                {
                    "id": str(student.id),
                    "first_name": student.first_name,
                    "last_name": student.last_name,
                    "email": student.email
                }
                for student in students
            ],
            "total": len(students)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get course students: {str(e)}"
        )
