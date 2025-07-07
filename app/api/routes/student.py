from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import structlog

from app.db.database import get_db
from app.db import crud, schemas
from app.api.dependencies import get_current_user, require_role, get_pagination_params
from app.exceptions.custom_exceptions import SMSException

logger = structlog.get_logger()
router = APIRouter()

# Student Profile Management
@router.get("/profile", response_model=schemas.UserResponse)
async def get_student_profile(
    current_user: schemas.User = Depends(require_role(["student"])),
    db: AsyncSession = Depends(get_db)
):
    """Get current student's profile"""
    return current_user

@router.put("/profile", response_model=schemas.UserResponse)
async def update_student_profile(
    profile_update: schemas.UserUpdate,
    current_user: schemas.User = Depends(require_role(["student"])),
    db: AsyncSession = Depends(get_db)
):
    """Update current student's profile"""
    try:
        updated_user = await crud.update_user(
            db, user_id=current_user.id, user_update=profile_update
        )
        logger.info("Student profile updated", student_id=current_user.id)
        return updated_user
    except Exception as e:
        logger.error("Failed to update student profile", error=str(e))
        raise SMSException("Failed to update profile", "PROFILE_UPDATE_ERROR")

# Student Classes
@router.get("/classes", response_model=List[schemas.ClassResponse])
async def get_student_classes(
    current_user: schemas.User = Depends(require_role(["student"])),
    db: AsyncSession = Depends(get_db)
):
    """Get all classes for current student"""
    try:
        classes = await crud.get_student_classes(db, student_id=current_user.id)
        return classes
    except Exception as e:
        logger.error("Failed to get student classes", error=str(e))
        raise SMSException("Failed to retrieve classes", "CLASSES_FETCH_ERROR")

@router.get("/classes/{class_id}", response_model=schemas.ClassResponse)
async def get_student_class_details(
    class_id: int,
    current_user: schemas.User = Depends(require_role(["student"])),
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific class for current student"""
    try:
        # Verify student is enrolled in this class
        class_obj = await crud.get_class_by_id(db, class_id=class_id)
        if not class_obj:
            raise HTTPException(status_code=404, detail="Class not found")
        
        # Check if student is enrolled
        enrollment = await crud.get_student_class_enrollment(
            db, student_id=current_user.id, class_id=class_id
        )
        if not enrollment:
            raise HTTPException(status_code=403, detail="Not enrolled in this class")
        
        return class_obj
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get class details", error=str(e))
        raise SMSException("Failed to retrieve class details", "CLASS_DETAILS_ERROR")

# Student Quizzes
@router.get("/quizzes", response_model=List[schemas.QuizResponse])
async def get_student_quizzes(
    class_id: Optional[int] = None,
    current_user: schemas.User = Depends(require_role(["student"])),
    db: AsyncSession = Depends(get_db),
    pagination: dict = Depends(get_pagination_params)
):
    """Get all quizzes available to current student"""
    try:
        quizzes = await crud.get_student_quizzes(
            db, 
            student_id=current_user.id, 
            class_id=class_id,
            skip=pagination["skip"],
            limit=pagination["limit"]
        )
        return quizzes
    except Exception as e:
        logger.error("Failed to get student quizzes", error=str(e))
        raise SMSException("Failed to retrieve quizzes", "QUIZZES_FETCH_ERROR")

@router.get("/quizzes/{quiz_id}", response_model=schemas.QuizResponse)
async def get_quiz_details(
    quiz_id: int,
    current_user: schemas.User = Depends(require_role(["student"])),
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific quiz"""
    try:
        quiz = await crud.get_quiz_by_id(db, quiz_id=quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Check if student has access to this quiz (enrolled in class)
        enrollment = await crud.get_student_class_enrollment(
            db, student_id=current_user.id, class_id=quiz.class_id
        )
        if not enrollment:
            raise HTTPException(status_code=403, detail="Not enrolled in quiz class")
        
        return quiz
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get quiz details", error=str(e))
        raise SMSException("Failed to retrieve quiz details", "QUIZ_DETAILS_ERROR")

@router.post("/quizzes/{quiz_id}/attempts", response_model=schemas.QuizAttemptResponse)
async def submit_quiz_attempt(
    quiz_id: int,
    attempt_data: schemas.QuizAttemptCreate,
    current_user: schemas.User = Depends(require_role(["student"])),
    db: AsyncSession = Depends(get_db)
):
    """Submit a quiz attempt"""
    try:
        # Verify quiz exists and student has access
        quiz = await crud.get_quiz_by_id(db, quiz_id=quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        enrollment = await crud.get_student_class_enrollment(
            db, student_id=current_user.id, class_id=quiz.class_id
        )
        if not enrollment:
            raise HTTPException(status_code=403, detail="Not enrolled in quiz class")
        
        # Check if quiz is still available
        if not quiz.is_active:
            raise HTTPException(status_code=400, detail="Quiz is not active")
        
        # Create attempt
        attempt_data.student_id = current_user.id
        attempt_data.quiz_id = quiz_id
        
        attempt = await crud.create_quiz_attempt(db, attempt=attempt_data)
        logger.info("Quiz attempt submitted", quiz_id=quiz_id, student_id=current_user.id)
        return attempt
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to submit quiz attempt", error=str(e))
        raise SMSException("Failed to submit quiz attempt", "QUIZ_ATTEMPT_ERROR")

@router.get("/quizzes/{quiz_id}/attempts", response_model=List[schemas.QuizAttemptResponse])
async def get_quiz_attempts(
    quiz_id: int,
    current_user: schemas.User = Depends(require_role(["student"])),
    db: AsyncSession = Depends(get_db)
):
    """Get all attempts for a specific quiz by current student"""
    try:
        attempts = await crud.get_student_quiz_attempts(
            db, student_id=current_user.id, quiz_id=quiz_id
        )
        return attempts
    except Exception as e:
        logger.error("Failed to get quiz attempts", error=str(e))
        raise SMSException("Failed to retrieve quiz attempts", "QUIZ_ATTEMPTS_ERROR")

# Student Attendance
@router.get("/attendance", response_model=List[schemas.AttendanceResponse])
async def get_student_attendance(
    class_id: Optional[int] = None,
    current_user: schemas.User = Depends(require_role(["student"])),
    db: AsyncSession = Depends(get_db),
    pagination: dict = Depends(get_pagination_params)
):
    """Get attendance records for current student"""
    try:
        attendance = await crud.get_student_attendance(
            db, 
            student_id=current_user.id, 
            class_id=class_id,
            skip=pagination["skip"],
            limit=pagination["limit"]
        )
        return attendance
    except Exception as e:
        logger.error("Failed to get student attendance", error=str(e))
        raise SMSException("Failed to retrieve attendance", "ATTENDANCE_FETCH_ERROR")

@router.get("/attendance/summary")
async def get_student_attendance_summary(
    class_id: Optional[int] = None,
    current_user: schemas.User = Depends(require_role(["student"])),
    db: AsyncSession = Depends(get_db)
):
    """Get attendance summary for current student"""
    try:
        summary = await crud.get_student_attendance_summary(
            db, student_id=current_user.id, class_id=class_id
        )
        return summary
    except Exception as e:
        logger.error("Failed to get attendance summary", error=str(e))
        raise SMSException("Failed to retrieve attendance summary", "ATTENDANCE_SUMMARY_ERROR")

# Student Grades/Results
@router.get("/grades")
async def get_student_grades(
    class_id: Optional[int] = None,
    current_user: schemas.User = Depends(require_role(["student"])),
    db: AsyncSession = Depends(get_db)
):
    """Get grades/results for current student"""
    try:
        grades = await crud.get_student_grades(
            db, student_id=current_user.id, class_id=class_id
        )
        return grades
    except Exception as e:
        logger.error("Failed to get student grades", error=str(e))
        raise SMSException("Failed to retrieve grades", "GRADES_FETCH_ERROR")
