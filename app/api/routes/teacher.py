from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import structlog

from app.api.dependencies import get_db, require_teacher, get_pagination_params, PaginationParams
from app.db import crud
from app.db.schemas import (
    QuizCreate, QuizUpdate, QuizResponse, QuizQuestionCreate, QuizQuestionUpdate,
    QuizQuestionResponse, APIResponse, ClassResponse, UserResponse
)
from app.exceptions.custom_exceptions import QuizNotFoundException, ClassNotFoundException

logger = structlog.get_logger()
router = APIRouter()


@router.get("/classes", response_model=List[ClassResponse])
async def get_my_classes(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    """Get classes taught by current teacher."""
    try:
        classes = await crud.class_.get_by_teacher(db, teacher_id=current_user.id)
        return classes
        
    except Exception as e:
        logger.error("Failed to get teacher classes", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve classes"
        )


@router.get("/classes/{class_id}/students", response_model=List[UserResponse])
async def get_class_students(
    class_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    """Get students in a specific class."""
    try:
        # Verify teacher owns this class
        class_obj = await crud.class_.get(db, id=class_id)
        if not class_obj or class_obj.teacher_id != current_user.id:
            raise ClassNotFoundException(str(class_id))
        
        students = await crud.class_.get_enrolled_students(db, class_id=class_id)
        return students
        
    except ClassNotFoundException:
        raise
    except Exception as e:
        logger.error("Failed to get class students", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve class students"
        )


@router.get("/quizzes", response_model=List[QuizResponse])
async def get_my_quizzes(
    class_id: UUID = None,
    pagination: PaginationParams = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    """Get quizzes created by current teacher."""
    try:
        if class_id:
            # Verify teacher owns this class
            class_obj = await crud.class_.get(db, id=class_id)
            if not class_obj or class_obj.teacher_id != current_user.id:
                raise ClassNotFoundException(str(class_id))
            
            quizzes = await crud.quiz.get_by_class(
                db, class_id=class_id, skip=pagination.skip, limit=pagination.limit
            )
        else:
            # Get all quizzes created by this teacher
            quizzes = await crud.quiz.get_multi(
                db, skip=pagination.skip, limit=pagination.limit, created_by=current_user.id
            )
        
        return quizzes
        
    except ClassNotFoundException:
        raise
    except Exception as e:
        logger.error("Failed to get teacher quizzes", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve quizzes"
        )


@router.post("/quizzes", response_model=QuizResponse)
async def create_quiz(
    quiz_data: QuizCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    """Create a new quiz."""
    try:
        # Verify teacher owns the class
        class_obj = await crud.class_.get(db, id=quiz_data.class_id)
        if not class_obj or class_obj.teacher_id != current_user.id:
            raise ClassNotFoundException(str(quiz_data.class_id))
        
        quiz = await crud.quiz.create(db, obj_in=quiz_data, creator_id=current_user.id)
        logger.info("Quiz created", quiz_id=str(quiz.id), teacher_id=str(current_user.id))
        return quiz
        
    except ClassNotFoundException:
        raise
    except Exception as e:
        logger.error("Failed to create quiz", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create quiz"
        )


@router.get("/quizzes/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    """Get quiz by ID."""
    quiz = await crud.quiz.get(db, id=quiz_id)
    if not quiz or quiz.created_by != current_user.id:
        raise QuizNotFoundException(str(quiz_id))
    return quiz


@router.put("/quizzes/{quiz_id}", response_model=QuizResponse)
async def update_quiz(
    quiz_id: UUID,
    quiz_update: QuizUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    """Update quiz."""
    quiz = await crud.quiz.get(db, id=quiz_id)
    if not quiz or quiz.created_by != current_user.id:
        raise QuizNotFoundException(str(quiz_id))
    
    updated_quiz = await crud.quiz.update(db, db_obj=quiz, obj_in=quiz_update.model_dump(exclude_unset=True))
    logger.info("Quiz updated", quiz_id=str(quiz_id), teacher_id=str(current_user.id))
    return updated_quiz


@router.post("/quizzes/{quiz_id}/questions", response_model=QuizQuestionResponse)
async def create_quiz_question(
    quiz_id: UUID,
    question_data: QuizQuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    """Add a question to a quiz."""
    try:
        # Verify teacher owns the quiz
        quiz = await crud.quiz.get(db, id=quiz_id)
        if not quiz or quiz.created_by != current_user.id:
            raise QuizNotFoundException(str(quiz_id))
        
        # Set quiz_id in question data
        question_data.quiz_id = quiz_id
        
        question = await crud.quiz_question.create(db, obj_in=question_data)
        logger.info("Quiz question created", question_id=str(question.id), quiz_id=str(quiz_id))
        return question
        
    except QuizNotFoundException:
        raise
    except Exception as e:
        logger.error("Failed to create quiz question", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create quiz question"
        )


@router.get("/quizzes/{quiz_id}/questions", response_model=List[QuizQuestionResponse])
async def get_quiz_questions(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    """Get all questions for a quiz."""
    # Verify teacher owns the quiz
    quiz = await crud.quiz.get(db, id=quiz_id)
    if not quiz or quiz.created_by != current_user.id:
        raise QuizNotFoundException(str(quiz_id))
    
    questions = await crud.quiz_question.get_by_quiz(db, quiz_id=quiz_id)
    return questions


@router.put("/quizzes/{quiz_id}/publish", response_model=APIResponse)
async def publish_quiz(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    """Publish a quiz to make it available to students."""
    quiz = await crud.quiz.get(db, id=quiz_id)
    if not quiz or quiz.created_by != current_user.id:
        raise QuizNotFoundException(str(quiz_id))
    
    # Verify quiz has questions
    questions = await crud.quiz_question.get_by_quiz(db, quiz_id=quiz_id)
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot publish quiz without questions"
        )
    
    await crud.quiz.update(
        db, 
        db_obj=quiz, 
        obj_in={"is_published": True, "status": "published"}
    )
    
    logger.info("Quiz published", quiz_id=str(quiz_id), teacher_id=str(current_user.id))
    return APIResponse(message="Quiz published successfully")


@router.get("/dashboard/stats")
async def get_teacher_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_teacher)
):
    """Get teacher dashboard statistics."""
    try:
        stats = {
            "my_classes": await crud.class_.count(db, teacher_id=current_user.id, is_active=True),
            "my_quizzes": await crud.quiz.count(db, created_by=current_user.id),
            "published_quizzes": await crud.quiz.count(db, created_by=current_user.id, is_published=True),
            "total_attempts": await crud.quiz_attempt.count(db),  # This would need a more complex query in real implementation
        }
        
        return APIResponse(data=stats)
        
    except Exception as e:
        logger.error("Failed to get teacher dashboard stats", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard statistics"
        )
