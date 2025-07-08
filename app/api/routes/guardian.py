from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import structlog

from app.db import crud, schemas
from app.api.dependencies import get_current_user, require_role, get_pagination_params, get_db
from app.exceptions.custom_exceptions import SMSException

logger = structlog.get_logger()
router = APIRouter()

# Guardian Profile Management
@router.get("/profile", response_model=schemas.UserResponse)
async def get_guardian_profile(
    current_user: schemas.UserResponse = Depends(require_role(["guardian"])),
    db: AsyncSession = Depends(get_db)
):
    """Get current guardian's profile"""
    return current_user

@router.put("/profile", response_model=schemas.UserResponse)
async def update_guardian_profile(
    profile_update: schemas.UserUpdate,
    current_user: schemas.UserResponse = Depends(require_role(["guardian"])),
    db: AsyncSession = Depends(get_db)
):
    """Update current guardian's profile"""
    try:
        updated_user = await crud.update_user(
            db, user_id=current_user.id, user_update=profile_update
        )
        logger.info("Guardian profile updated", guardian_id=current_user.id)
        return updated_user
    except Exception as e:
        logger.error("Failed to update guardian profile", error=str(e))
        raise SMSException("Failed to update profile", "PROFILE_UPDATE_ERROR")

# Guardian's Students Management
@router.get("/students", response_model=List[schemas.UserResponse])
async def get_guardian_students(
    current_user: schemas.UserResponse = Depends(require_role(["guardian"])),
    db: AsyncSession = Depends(get_db)
):
    """Get all students under current guardian"""
    try:
        students = await crud.get_guardian_students(db, guardian_id=current_user.id)
        return students
    except Exception as e:
        logger.error("Failed to get guardian students", error=str(e))
        raise SMSException("Failed to retrieve students", "STUDENTS_FETCH_ERROR")

@router.get("/students/{student_id}", response_model=schemas.UserResponse)
async def get_student_details(
    student_id: int,
    current_user: schemas.UserResponse = Depends(require_role(["guardian"])),
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific student under current guardian"""
    try:
        # Verify guardian has access to this student
        guardian_student = await crud.get_guardian_student_relationship(
            db, guardian_id=current_user.id, student_id=student_id
        )
        if not guardian_student:
            raise HTTPException(status_code=403, detail="Not authorized to view this student")
        
        student = await crud.get_user_by_id(db, user_id=student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return student
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get student details", error=str(e))
        raise SMSException("Failed to retrieve student details", "STUDENT_DETAILS_ERROR")

# Student Classes (viewed by guardian)
@router.get("/students/{student_id}/classes", response_model=List[schemas.ClassResponse])
async def get_student_classes(
    student_id: int,
    current_user: schemas.UserResponse = Depends(require_role(["guardian"])),
    db: AsyncSession = Depends(get_db)
):
    """Get all classes for a specific student under current guardian"""
    try:
        # Verify guardian has access to this student
        guardian_student = await crud.get_guardian_student_relationship(
            db, guardian_id=current_user.id, student_id=student_id
        )
        if not guardian_student:
            raise HTTPException(status_code=403, detail="Not authorized to view this student")
        
        classes = await crud.get_student_classes(db, student_id=student_id)
        return classes
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get student classes", error=str(e))
        raise SMSException("Failed to retrieve classes", "CLASSES_FETCH_ERROR")

# Student Attendance (viewed by guardian)
@router.get("/students/{student_id}/attendance", response_model=List[schemas.AttendanceResponse])
async def get_student_attendance(
    student_id: int,
    class_id: Optional[int] = None,
    current_user: schemas.UserResponse = Depends(require_role(["guardian"])),
    db: AsyncSession = Depends(get_db),
    pagination: dict = Depends(get_pagination_params)
):
    """Get attendance records for a specific student under current guardian"""
    try:
        # Verify guardian has access to this student
        guardian_student = await crud.get_guardian_student_relationship(
            db, guardian_id=current_user.id, student_id=student_id
        )
        if not guardian_student:
            raise HTTPException(status_code=403, detail="Not authorized to view this student")
        
        attendance = await crud.get_student_attendance(
            db, 
            student_id=student_id, 
            class_id=class_id,
            skip=pagination["skip"],
            limit=pagination["limit"]
        )
        return attendance
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get student attendance", error=str(e))
        raise SMSException("Failed to retrieve attendance", "ATTENDANCE_FETCH_ERROR")

@router.get("/students/{student_id}/attendance/summary")
async def get_student_attendance_summary(
    student_id: int,
    class_id: Optional[int] = None,
    current_user: schemas.UserResponse = Depends(require_role(["guardian"])),
    db: AsyncSession = Depends(get_db)
):
    """Get attendance summary for a specific student under current guardian"""
    try:
        # Verify guardian has access to this student
        guardian_student = await crud.get_guardian_student_relationship(
            db, guardian_id=current_user.id, student_id=student_id
        )
        if not guardian_student:
            raise HTTPException(status_code=403, detail="Not authorized to view this student")
        
        summary = await crud.get_student_attendance_summary(
            db, student_id=student_id, class_id=class_id
        )
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get attendance summary", error=str(e))
        raise SMSException("Failed to retrieve attendance summary", "ATTENDANCE_SUMMARY_ERROR")

# Student Grades/Results (viewed by guardian)
@router.get("/students/{student_id}/grades")
async def get_student_grades(
    student_id: int,
    class_id: Optional[int] = None,
    current_user: schemas.UserResponse = Depends(require_role(["guardian"])),
    db: AsyncSession = Depends(get_db)
):
    """Get grades/results for a specific student under current guardian"""
    try:
        # Verify guardian has access to this student
        guardian_student = await crud.get_guardian_student_relationship(
            db, guardian_id=current_user.id, student_id=student_id
        )
        if not guardian_student:
            raise HTTPException(status_code=403, detail="Not authorized to view this student")
        
        grades = await crud.get_student_grades(
            db, student_id=student_id, class_id=class_id
        )
        return grades
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get student grades", error=str(e))
        raise SMSException("Failed to retrieve grades", "GRADES_FETCH_ERROR")

# Student Quiz Results (viewed by guardian)
@router.get("/students/{student_id}/quizzes", response_model=List[schemas.QuizAttemptResponse])
async def get_student_quiz_attempts(
    student_id: int,
    class_id: Optional[int] = None,
    current_user: schemas.UserResponse = Depends(require_role(["guardian"])),
    db: AsyncSession = Depends(get_db),
    pagination: dict = Depends(get_pagination_params)
):
    """Get quiz attempts for a specific student under current guardian"""
    try:
        # Verify guardian has access to this student
        guardian_student = await crud.get_guardian_student_relationship(
            db, guardian_id=current_user.id, student_id=student_id
        )
        if not guardian_student:
            raise HTTPException(status_code=403, detail="Not authorized to view this student")
        
        attempts = await crud.get_student_quiz_attempts(
            db, student_id=student_id, class_id=class_id,
            skip=pagination["skip"], limit=pagination["limit"]
        )
        return attempts
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get student quiz attempts", error=str(e))
        raise SMSException("Failed to retrieve quiz attempts", "QUIZ_ATTEMPTS_ERROR")

# Communication/Messages (placeholder for future implementation)
@router.get("/messages")
async def get_guardian_messages(
    current_user: schemas.UserResponse = Depends(require_role(["guardian"])),
    db: AsyncSession = Depends(get_db)
):
    """Get messages/communications for current guardian"""
    # This would be implemented in a future version
    return {"message": "Communication system not yet implemented"}

@router.post("/messages")
async def send_message(
    current_user: schemas.UserResponse = Depends(require_role(["guardian"])),
    db: AsyncSession = Depends(get_db)
):
    """Send a message to school/teacher"""
    # This would be implemented in a future version
    return {"message": "Communication system not yet implemented"}

# Reports and Analytics
@router.get("/reports/overview")
async def get_guardian_overview(
    current_user: schemas.UserResponse = Depends(require_role(["guardian"])),
    db: AsyncSession = Depends(get_db)
):
    """Get overview report for all students under current guardian"""
    try:
        overview = await crud.get_guardian_overview(db, guardian_id=current_user.id)
        return overview
    except Exception as e:
        logger.error("Failed to get guardian overview", error=str(e))
        raise SMSException("Failed to retrieve overview", "OVERVIEW_ERROR")

@router.get("/reports/students/{student_id}/performance")
async def get_student_performance_report(
    student_id: int,
    current_user: schemas.UserResponse = Depends(require_role(["guardian"])),
    db: AsyncSession = Depends(get_db)
):
    """Get performance report for a specific student"""
    try:
        # Verify guardian has access to this student
        guardian_student = await crud.get_guardian_student_relationship(
            db, guardian_id=current_user.id, student_id=student_id
        )
        if not guardian_student:
            raise HTTPException(status_code=403, detail="Not authorized to view this student")
        
        performance = await crud.get_student_performance_report(
            db, student_id=student_id
        )
        return performance
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get student performance report", error=str(e))
        raise SMSException("Failed to retrieve performance report", "PERFORMANCE_REPORT_ERROR")
