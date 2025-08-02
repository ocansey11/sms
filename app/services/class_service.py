from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
from uuid import UUID
from fastapi import HTTPException

from app.db import crud, schemas
from app.db.models import Course, StudentEnrollment, User, Quiz, QuizAttempt
from app.exceptions.custom_exceptions import SMSException


class CourseService:
    """Course management service"""
    
    @staticmethod
    async def create_course(
        db: AsyncSession, 
        course_create: schemas.CourseCreate,
        creator_id: UUID
    ) -> Course:
        """Create a new course"""
        try:
            # Verify user has permission to create courses
            if course_create.organization_id:
                # For organization courses, check org permissions
                has_permission = await crud.user_role.user_has_role(
                    db, 
                    user_id=creator_id, 
                    role="org_owner",
                    organization_id=course_create.organization_id
                ) or await crud.user_role.user_has_role(
                    db, 
                    user_id=creator_id, 
                    role="org_admin",
                    organization_id=course_create.organization_id
                )
                if not has_permission:
                    raise HTTPException(status_code=403, detail="Insufficient permissions")
            else:
                # For solo teacher courses, check solo teacher permission
                has_permission = await crud.user_role.user_has_role(
                    db, 
                    user_id=creator_id, 
                    role="solo_teacher"
                )
                if not has_permission:
                    raise HTTPException(status_code=403, detail="Only solo teachers can create personal courses")
            
            course = await crud.course.create(db, obj_in=course_create)
            return course
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Course creation failed: {str(e)}")
    
    @staticmethod
    async def get_course_by_id(db: AsyncSession, course_id: UUID) -> Optional[Course]:
        """Get course by ID"""
        return await crud.course.get(db, id=course_id)
    
    @staticmethod
    async def get_organization_courses(
        db: AsyncSession,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Course]:
        """Get courses by organization"""
        return await crud.course.get_by_organization(
            db, organization_id=organization_id, skip=skip, limit=limit
        )
    
    @staticmethod
    async def get_teacher_courses(
        db: AsyncSession,
        teacher_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Course]:
        """Get courses taught by a teacher"""
        # For solo teachers, get courses where solo_teacher_id matches
        # For org teachers, get courses through TeacherCourse assignments
        solo_courses = await crud.course.get_multi(
            db, skip=skip, limit=limit, solo_teacher_id=teacher_id
        )
        
        # TODO: Add logic to get organization courses assigned to teacher
        # This would require joining with TeacherCourse table
        
        return solo_courses
    
    @staticmethod
    async def enroll_student(
        db: AsyncSession,
        course_id: UUID,
        student_id: UUID,
        enrolling_user_id: UUID
    ) -> StudentEnrollment:
        """Enroll a student in a course"""
        try:
            # Verify course exists
            course = await crud.course.get(db, id=course_id)
            if not course:
                raise HTTPException(status_code=404, detail="Course not found")
            
            # Verify enrolling user has permission
            if course.organization_id:
                # Organization course - check org permissions
                has_permission = await crud.user_role.user_has_role(
                    db, enrolling_user_id, "org_admin", course.organization_id
                ) or await crud.user_role.user_has_role(
                    db, enrolling_user_id, "org_owner", course.organization_id
                )
            else:
                # Solo teacher course - check if enrolling user is the teacher
                has_permission = course.solo_teacher_id == enrolling_user_id
            
            if not has_permission:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            # Create enrollment
            enrollment = await crud.course.enroll_student(
                db, course_id=course_id, student_id=student_id
            )
            return enrollment
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Student enrollment failed: {str(e)}")
    
    @staticmethod
    async def get_course_students(db: AsyncSession, course_id: UUID) -> List[User]:
        """Get students enrolled in a course"""
        try:
            return await crud.course.get_enrolled_students(db, course_id=course_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get course students: {str(e)}")
    
    @staticmethod
    async def get_student_courses(db: AsyncSession, student_id: UUID) -> List[Course]:
        """Get all courses for a student"""
        try:
            return await crud.get_student_courses(db, student_id=student_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get student courses: {str(e)}")
    
    @staticmethod
    async def get_course_statistics(db: AsyncSession, course_id: UUID) -> Dict[str, Any]:
        """Get course statistics"""
        try:
            return await crud.get_course_statistics(db, course_id=course_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get course statistics: {str(e)}")


class QuizService:
    """Quiz management service"""
    
    @staticmethod
    async def create_quiz(
        db: AsyncSession,
        quiz_create: schemas.QuizCreate,
        creator_id: UUID
    ) -> Quiz:
        """Create a new quiz"""
        try:
            # Verify course exists and user has permission
            course = await crud.course.get(db, id=quiz_create.course_id)
            if not course:
                raise HTTPException(status_code=404, detail="Course not found")
            
            # Check permissions
            if course.organization_id:
                has_permission = await crud.user_role.user_has_role(
                    db, creator_id, "org_teacher", course.organization_id
                ) or await crud.user_role.user_has_role(
                    db, creator_id, "org_admin", course.organization_id
                ) or await crud.user_role.user_has_role(
                    db, creator_id, "org_owner", course.organization_id
                )
            else:
                has_permission = course.solo_teacher_id == creator_id
            
            if not has_permission:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            quiz = await crud.quiz.create(db, obj_in=quiz_create, creator_id=creator_id)
            return quiz
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Quiz creation failed: {str(e)}")
    
    @staticmethod
    async def get_quiz_by_id(db: AsyncSession, quiz_id: UUID) -> Optional[Quiz]:
        """Get quiz by ID"""
        return await crud.quiz.get(db, id=quiz_id)
    
    @staticmethod
    async def get_course_quizzes(
        db: AsyncSession,
        course_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Quiz]:
        """Get quizzes for a course"""
        return await crud.quiz.get_by_class(db, class_id=course_id, skip=skip, limit=limit)
    
    @staticmethod
    async def start_quiz_attempt(
        db: AsyncSession,
        quiz_id: UUID,
        student_id: UUID
    ) -> QuizAttempt:
        """Start a new quiz attempt"""
        try:
            # Verify quiz exists
            quiz = await crud.quiz.get(db, id=quiz_id)
            if not quiz:
                raise HTTPException(status_code=404, detail="Quiz not found")
            
            # Check if student is enrolled in the course
            enrollment = await crud.get_student_enrollment(
                db, student_id=student_id, course_id=quiz.course_id
            )
            if not enrollment:
                raise HTTPException(status_code=403, detail="Student not enrolled in course")
            
            # Check for existing active attempt
            active_attempt = await crud.quiz_attempt.get_active_attempt(
                db, student_id=student_id, quiz_id=quiz_id
            )
            if active_attempt:
                raise HTTPException(status_code=400, detail="Active attempt already exists")
            
            # Create new attempt
            attempt_data = schemas.QuizAttemptCreate(quiz_id=quiz_id)
            attempt = await crud.quiz_attempt.create(
                db, obj_in=attempt_data, student_id=student_id
            )
            return attempt
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to start quiz attempt: {str(e)}")
    
    @staticmethod
    async def submit_quiz_attempt(
        db: AsyncSession,
        attempt_id: UUID,
        answers: Dict[str, Any]
    ) -> QuizAttempt:
        """Submit and grade quiz attempt"""
        try:
            # Get attempt
            attempt = await crud.quiz_attempt.get(db, id=attempt_id)
            if not attempt:
                raise HTTPException(status_code=404, detail="Quiz attempt not found")
            
            # Get quiz with questions
            quiz = await crud.quiz.get_with_questions(db, id=attempt.quiz_id)
            if not quiz:
                raise HTTPException(status_code=404, detail="Quiz not found")
            
            # Grade the attempt (simplified grading logic)
            total_questions = len(quiz.questions)
            correct_answers = 0
            
            for question in quiz.questions:
                student_answer = answers.get(str(question.id))
                if student_answer == question.correct_answer:
                    correct_answers += 1
            
            score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
            
            # Update attempt
            attempt.answers = answers
            attempt.score = score
            attempt.submitted_at = datetime.utcnow()
            attempt.status = "completed"
            
            await db.commit()
            await db.refresh(attempt)
            
            return attempt
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to submit quiz attempt: {str(e)}")
    
    @staticmethod
    async def get_student_quiz_attempts(
        db: AsyncSession,
        student_id: UUID,
        quiz_id: Optional[UUID] = None,
        course_id: Optional[UUID] = None
    ) -> List[QuizAttempt]:
        """Get quiz attempts for a student"""
        try:
            return await crud.get_student_quiz_attempts(
                db, student_id=student_id, quiz_id=quiz_id, class_id=course_id
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get quiz attempts: {str(e)}")
            raise
        except Exception as e:
            logger.error("Teacher assignment failed", error=str(e))
            raise SMSException("Teacher assignment failed", "TEACHER_ASSIGNMENT_ERROR")
    
    @staticmethod
    async def enroll_student_in_course(
        db: AsyncSession,
        enrollment_data: schemas.StudentEnrollmentCreate,
        enroller_id: UUID
    ) -> schemas.StudentEnrollmentResponse:
        """Enroll a student in a course"""
        try:
            # Verify course exists
            course = await crud.get_course_by_id(db, course_id=enrollment_data.course_id)
            if not course:
                raise SMSException("Course not found", "COURSE_NOT_FOUND")
            
            # Verify student exists and has access to this organization
            student_profile = await crud.get_student_profile(
                db,
                student_id=enrollment_data.student_id,
                organization_id=course.organization_id
            )
            if not student_profile:
                raise SMSException("Student not found in organization", "STUDENT_NOT_FOUND")
            
            # Verify enroller has permission
            has_permission = await crud.user_has_org_permission(
                db,
                user_id=enroller_id,
                organization_id=course.organization_id,
                required_roles=["org_owner", "org_admin", "org_teacher"]
            )
            if not has_permission:
                raise SMSException("Insufficient permissions", "PERMISSION_DENIED")
            
            # Check if already enrolled
            existing = await crud.get_student_enrollment(
                db,
                student_id=enrollment_data.student_id,
                course_id=enrollment_data.course_id
            )
            if existing and existing.status == "active":
                raise SMSException("Student already enrolled in course", "ALREADY_ENROLLED")
            
            # Create or reactivate enrollment
            if existing:
                # Reactivate existing enrollment
                enrollment = await crud.update_student_enrollment(
                    db,
                    student_id=enrollment_data.student_id,
                    course_id=enrollment_data.course_id,
                    update_data=schemas.StudentEnrollmentUpdate(status="active")
                )
            else:
                # Create new enrollment
                enrollment = await crud.create_student_enrollment(db, enrollment_data)
            
            logger.info("Student enrolled in course", 
                       student_id=enrollment_data.student_id, 
                       course_id=enrollment_data.course_id)
            return enrollment
        except SMSException:
            raise
        except Exception as e:
            logger.error("Student enrollment failed", error=str(e))
            raise SMSException("Student enrollment failed", "ENROLLMENT_ERROR")
    
    @staticmethod
    async def get_course_students(
        db: AsyncSession,
        course_id: UUID,
        requester_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[schemas.StudentEnrollmentResponse]:
        """Get all students enrolled in a course"""
        try:
            # Verify course exists
            course = await crud.get_course_by_id(db, course_id=course_id)
            if not course:
                raise SMSException("Course not found", "COURSE_NOT_FOUND")
            
            # Verify requester has permission
            has_permission = await crud.user_has_course_access(
                db,
                user_id=requester_id,
                course_id=course_id
            )
            if not has_permission:
                raise SMSException("Insufficient permissions", "PERMISSION_DENIED")
            
            students = await crud.get_course_students(
                db,
                course_id=course_id,
                skip=skip,
                limit=limit
            )
            return students
        except SMSException:
            raise
        except Exception as e:
            logger.error("Failed to get course students", error=str(e))
            raise SMSException("Failed to retrieve course students", "STUDENTS_FETCH_ERROR")
    
    @staticmethod
    async def get_course_statistics(
        db: AsyncSession,
        course_id: UUID,
        requester_id: UUID
    ) -> Dict[str, Any]:
        """Get statistics for a course"""
        try:
            # Verify course exists and user has access
            course = await crud.get_course_by_id(db, course_id=course_id)
            if not course:
                raise SMSException("Course not found", "COURSE_NOT_FOUND")
            
            has_permission = await crud.user_has_course_access(
                db,
                user_id=requester_id,
                course_id=course_id
            )
            if not has_permission:
                raise SMSException("Insufficient permissions", "PERMISSION_DENIED")
            
            stats = await crud.get_course_statistics(db, course_id=course_id)
            return stats
        except SMSException:
            raise
        except Exception as e:
            logger.error("Failed to get course statistics", error=str(e))
            raise SMSException("Failed to retrieve course statistics", "COURSE_STATS_ERROR")


class QuestionBankService:
    """Question bank management service"""
    
    @staticmethod
    async def create_question(
        db: AsyncSession,
        question_create: schemas.QuestionBankCreate,
        creator_id: UUID
    ) -> schemas.QuestionBankResponse:
        """Create a new question in the question bank"""
        try:
            # Verify creator has permission
            if question_create.organization_id:
                has_permission = await crud.user_has_org_permission(
                    db,
                    user_id=creator_id,
                    organization_id=question_create.organization_id,
                    required_roles=["org_owner", "org_admin", "org_teacher"]
                )
                if not has_permission:
                    raise SMSException("Insufficient permissions", "PERMISSION_DENIED")
            elif question_create.solo_teacher_id:
                if creator_id != question_create.solo_teacher_id:
                    raise SMSException("Insufficient permissions", "PERMISSION_DENIED")
            else:
                raise SMSException("Must specify organization or solo teacher", "INVALID_PROVIDER")
            
            # Validate question type specific fields
            if question_create.qtype == "mcq":
                if not question_create.options or len(question_create.options) < 2:
                    raise SMSException("MCQ questions must have at least 2 options", "INVALID_OPTIONS")
                if question_create.correct_answer is None or question_create.correct_answer >= len(question_create.options):
                    raise SMSException("Invalid correct answer index", "INVALID_ANSWER")
            elif question_create.qtype == "true_false":
                if question_create.correct_answer not in [0, 1]:
                    raise SMSException("True/False questions must have correct_answer as 0 or 1", "INVALID_ANSWER")
            
            question = await crud.create_question_bank_entry(db, question_create)
            logger.info("Question created successfully", question_id=question.id, qtype=question.qtype)
            return question
        except SMSException:
            raise
        except Exception as e:
            logger.error("Question creation failed", error=str(e))
            raise SMSException("Question creation failed", "QUESTION_CREATION_ERROR")
    
    @staticmethod
    async def get_questions(
        db: AsyncSession,
        organization_id: Optional[UUID] = None,
        solo_teacher_id: Optional[UUID] = None,
        qtype: Optional[str] = None,
        tags: Optional[List[str]] = None,
        requester_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[schemas.QuestionBankResponse]:
        """Get questions from the question bank with filters"""
        try:
            # Verify requester has permission if specified
            if requester_id:
                if organization_id:
                    has_permission = await crud.user_has_org_permission(
                        db,
                        user_id=requester_id,
                        organization_id=organization_id,
                        required_roles=["org_owner", "org_admin", "org_teacher"]
                    )
                    if not has_permission:
                        raise SMSException("Insufficient permissions", "PERMISSION_DENIED")
                elif solo_teacher_id:
                    if requester_id != solo_teacher_id:
                        raise SMSException("Insufficient permissions", "PERMISSION_DENIED")
            
            questions = await crud.get_questions_from_bank(
                db,
                organization_id=organization_id,
                solo_teacher_id=solo_teacher_id,
                qtype=qtype,
                tags=tags,
                skip=skip,
                limit=limit
            )
            return questions
        except SMSException:
            raise
        except Exception as e:
            logger.error("Failed to get questions", error=str(e))
            raise SMSException("Failed to retrieve questions", "QUESTIONS_FETCH_ERROR")


class QuizService:
    """Quiz management service"""
    
    @staticmethod
    async def create_quiz(
        db: AsyncSession, 
        quiz_create: schemas.QuizCreate,
        creator_id: UUID
    ) -> schemas.QuizResponse:
        """Create a new quiz"""
        try:
            # Verify course exists
            course = await crud.get_course_by_id(db, course_id=quiz_create.course_id)
            if not course:
                raise SMSException("Course not found", "COURSE_NOT_FOUND")
            
            # Verify creator has permission to create quizzes for this course
            has_permission = await crud.user_has_course_access(
                db,
                user_id=creator_id,
                course_id=quiz_create.course_id,
                required_roles=["org_owner", "org_admin", "org_teacher"]
            )
            if not has_permission:
                raise SMSException("Insufficient permissions", "PERMISSION_DENIED")
            
            quiz = await crud.create_quiz(db, quiz_create=quiz_create)
            logger.info("Quiz created successfully", quiz_id=quiz.id, course_id=quiz.course_id)
            return quiz
        except SMSException:
            raise
        except Exception as e:
            logger.error("Quiz creation failed", error=str(e))
            raise SMSException("Quiz creation failed", "QUIZ_CREATION_ERROR")
    
    @staticmethod
    async def add_question_to_quiz(
        db: AsyncSession,
        quiz_question_create: schemas.QuizQuestionCreate,
        creator_id: UUID
    ) -> schemas.QuizQuestionResponse:
        """Add a question from the question bank to a quiz"""
        try:
            # Verify quiz exists
            quiz = await crud.get_quiz_by_id(db, quiz_id=quiz_question_create.quiz_id)
            if not quiz:
                raise SMSException("Quiz not found", "QUIZ_NOT_FOUND")
            
            # Verify question exists
            question = await crud.get_question_bank_entry(db, question_id=quiz_question_create.question_id)
            if not question:
                raise SMSException("Question not found", "QUESTION_NOT_FOUND")
            
            # Verify creator has permission
            has_permission = await crud.user_has_course_access(
                db,
                user_id=creator_id,
                course_id=quiz.course_id,
                required_roles=["org_owner", "org_admin", "org_teacher"]
            )
            if not has_permission:
                raise SMSException("Insufficient permissions", "PERMISSION_DENIED")
            
            # Check if question already added to quiz
            existing = await crud.get_quiz_question_link(
                db,
                quiz_id=quiz_question_create.quiz_id,
                question_id=quiz_question_create.question_id
            )
            if existing:
                raise SMSException("Question already added to quiz", "QUESTION_EXISTS")
            
            # Add question to quiz
            quiz_question = await crud.create_quiz_question_link(db, quiz_question_create)
            logger.info("Question added to quiz", 
                       quiz_id=quiz_question_create.quiz_id, 
                       question_id=quiz_question_create.question_id)
            return quiz_question
        except SMSException:
            raise
        except Exception as e:
            logger.error("Failed to add question to quiz", error=str(e))
            raise SMSException("Failed to add question to quiz", "QUIZ_QUESTION_ERROR")
    
    @staticmethod
    async def start_quiz_attempt(
        db: AsyncSession,
        quiz_id: UUID,
        student_id: UUID
    ) -> schemas.QuizAttemptResponse:
        """Start a new quiz attempt"""
        try:
            # Verify quiz exists and is published
            quiz = await crud.get_quiz_by_id(db, quiz_id=quiz_id)
            if not quiz:
                raise SMSException("Quiz not found", "QUIZ_NOT_FOUND")
            
            if not quiz.published_at:
                raise SMSException("Quiz is not published", "QUIZ_NOT_PUBLISHED")
            
            # Verify student is enrolled in the course
            enrollment = await crud.get_student_enrollment(
                db,
                student_id=student_id,
                course_id=quiz.course_id
            )
            if not enrollment or enrollment.status != "active":
                raise SMSException("Student not enrolled in course", "NOT_ENROLLED")
            
            # Check if student has exceeded maximum attempts (if there's a limit)
            # This would need to be implemented based on quiz settings
            
            # Create new attempt
            attempt_data = schemas.QuizAttemptCreate(quiz_id=quiz_id)
            attempt = await crud.create_quiz_attempt(db, student_id=student_id, attempt_data=attempt_data)
            
            logger.info("Quiz attempt started", 
                       attempt_id=attempt.id, 
                       quiz_id=quiz_id, 
                       student_id=student_id)
            return attempt
        except SMSException:
            raise
        except Exception as e:
            logger.error("Failed to start quiz attempt", error=str(e))
            raise SMSException("Failed to start quiz attempt", "ATTEMPT_START_ERROR")
    
    @staticmethod
    async def submit_quiz_attempt(
        db: AsyncSession,
        attempt_id: UUID,
        student_id: UUID,
        answers: List[Dict[str, Any]]
    ) -> schemas.QuizAttemptResponse:
        """Submit and grade a quiz attempt"""
        try:
            # Verify attempt exists and belongs to student
            attempt = await crud.get_quiz_attempt_by_id(db, attempt_id=attempt_id)
            if not attempt:
                raise SMSException("Quiz attempt not found", "ATTEMPT_NOT_FOUND")
            
            if attempt.student_id != student_id:
                raise SMSException("Unauthorized access to attempt", "UNAUTHORIZED_ATTEMPT")
            
            if attempt.status != "in_progress":
                raise SMSException("Attempt already completed", "ATTEMPT_COMPLETED")
            
            # Get quiz questions for grading
            quiz_questions = await crud.get_quiz_questions(db, quiz_id=attempt.quiz_id)
            
            # Grade the attempt
            total_points = 0
            earned_points = 0
            graded_answers = []
            
            for answer in answers:
                question_id = answer.get("question_id")
                student_answer = answer.get("answer")
                
                # Find the question
                quiz_question = next(
                    (qq for qq in quiz_questions if str(qq.question_id) == str(question_id)), 
                    None
                )
                
                if not quiz_question:
                    continue
                
                question = quiz_question.question
                points = quiz_question.points
                total_points += points
                
                # Grade based on question type
                is_correct = False
                if question.qtype in ["mcq", "true_false"]:
                    is_correct = student_answer == question.correct_answer
                elif question.qtype == "short_answer":
                    # Simple string comparison - could be enhanced with fuzzy matching
                    is_correct = str(student_answer).strip().lower() == str(question.correct_answer).strip().lower()
                # Essay questions would need manual grading
                
                if is_correct:
                    earned_points += points
                
                graded_answers.append({
                    "question_id": question_id,
                    "student_answer": student_answer,
                    "correct_answer": question.correct_answer,
                    "is_correct": is_correct,
                    "points_earned": points if is_correct else 0,
                    "points_possible": points
                })
            
            # Calculate final score
            percentage = (earned_points / total_points * 100) if total_points > 0 else 0
            
            # Update attempt
            update_data = schemas.QuizAttemptUpdate(
                answers=graded_answers,
                status="completed",
                finished_at=datetime.utcnow(),
                score=earned_points,
                percentage=percentage
            )
            
            updated_attempt = await crud.update_quiz_attempt(
                db,
                attempt_id=attempt_id,
                update_data=update_data
            )
            
            logger.info("Quiz attempt submitted and graded", 
                       attempt_id=attempt_id, 
                       score=earned_points,
                       percentage=percentage)
            return updated_attempt
        except SMSException:
            raise
        except Exception as e:
            logger.error("Failed to submit quiz attempt", error=str(e))
            raise SMSException("Failed to submit quiz attempt", "ATTEMPT_SUBMIT_ERROR")
    
    @staticmethod
    async def get_quiz_attempts(
        db: AsyncSession,
        quiz_id: UUID,
        requester_id: UUID,
        student_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[schemas.QuizAttemptResponse]:
        """Get quiz attempts with filtering"""
        try:
            # Verify quiz exists
            quiz = await crud.get_quiz_by_id(db, quiz_id=quiz_id)
            if not quiz:
                raise SMSException("Quiz not found", "QUIZ_NOT_FOUND")
            
            # Verify requester has permission
            has_permission = await crud.user_has_course_access(
                db,
                user_id=requester_id,
                course_id=quiz.course_id
            )
            if not has_permission:
                raise SMSException("Insufficient permissions", "PERMISSION_DENIED")
            
            attempts = await crud.get_quiz_attempts(
                db,
                quiz_id=quiz_id,
                student_id=student_id,
                skip=skip,
                limit=limit
            )
            return attempts
        except SMSException:
            raise
        except Exception as e:
            logger.error("Failed to get quiz attempts", error=str(e))
            raise SMSException("Failed to retrieve quiz attempts", "ATTEMPTS_FETCH_ERROR")


class ReportService:
    """Reporting and analytics service"""
    
    @staticmethod
    async def generate_student_performance_report(
        db: AsyncSession,
        student_id: UUID,
        organization_id: Optional[UUID] = None,
        solo_teacher_id: Optional[UUID] = None,
        requester_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive performance report for a student"""
        try:
            # Verify student exists
            student = await crud.get_user_by_id(db, user_id=student_id)
            if not student:
                raise SMSException("Student not found", "STUDENT_NOT_FOUND")
            
            # Verify requester has permission if specified
            if requester_id:
                if organization_id:
                    has_permission = await crud.user_has_org_permission(
                        db,
                        user_id=requester_id,
                        organization_id=organization_id,
                        required_roles=["org_owner", "org_admin", "org_teacher"]
                    )
                    if not has_permission:
                        # Check if requester is guardian
                        is_guardian = await crud.is_student_guardian(
                            db,
                            guardian_id=requester_id,
                            student_id=student_id
                        )
                        if not is_guardian:
                            raise SMSException("Insufficient permissions", "PERMISSION_DENIED")
            
            # Get student enrollments
            enrollments = await crud.get_student_enrollments(
                db,
                student_id=student_id,
                organization_id=organization_id,
                solo_teacher_id=solo_teacher_id
            )
            
            # Get quiz performance
            quiz_performance = await crud.get_student_quiz_performance(
                db,
                student_id=student_id,
                organization_id=organization_id,
                solo_teacher_id=solo_teacher_id
            )
            
            report = {
                "student_info": {
                    "id": student.id,
                    "name": student.full_name,
                    "email": student.email
                },
                "enrollments": enrollments,
                "quiz_performance": quiz_performance,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info("Student performance report generated", student_id=student_id)
            return report
        except SMSException:
            raise
        except Exception as e:
            logger.error("Failed to generate student performance report", error=str(e))
            raise SMSException("Report generation failed", "REPORT_ERROR")
    
    @staticmethod
    async def generate_course_analytics(
        db: AsyncSession,
        course_id: UUID,
        requester_id: UUID
    ) -> Dict[str, Any]:
        """Generate analytics for a course"""
        try:
            # Verify course exists and user has access
            course = await crud.get_course_by_id(db, course_id=course_id)
            if not course:
                raise SMSException("Course not found", "COURSE_NOT_FOUND")
            
            has_permission = await crud.user_has_course_access(
                db,
                user_id=requester_id,
                course_id=course_id
            )
            if not has_permission:
                raise SMSException("Insufficient permissions", "PERMISSION_DENIED")
            
            # Get course statistics
            stats = await crud.get_course_analytics(db, course_id=course_id)
            
            analytics = {
                "course_info": {
                    "id": course.id,
                    "title": course.title,
                    "organization_id": course.organization_id
                },
                "statistics": stats,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info("Course analytics generated", course_id=course_id)
            return analytics
        except SMSException:
            raise
        except Exception as e:
            logger.error("Failed to generate course analytics", error=str(e))
            raise SMSException("Analytics generation failed", "ANALYTICS_ERROR")