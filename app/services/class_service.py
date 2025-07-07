from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
import structlog

from app.db import crud, schemas
from app.exceptions.custom_exceptions import SMSException

logger = structlog.get_logger()

class ClassService:
    """Class management service"""
    
    @staticmethod
    async def create_class(db: AsyncSession, class_create: schemas.ClassCreate) -> schemas.Class:
        """Create a new class"""
        try:
            # Check if class with same name already exists
            existing_class = await crud.get_class_by_name(db, name=class_create.name)
            if existing_class:
                raise SMSException("Class with this name already exists", "CLASS_EXISTS")
            
            class_obj = await crud.create_class(db, class_create=class_create)
            logger.info("Class created successfully", class_id=class_obj.id, name=class_obj.name)
            return class_obj
        except SMSException:
            raise
        except Exception as e:
            logger.error("Class creation failed", error=str(e))
            raise SMSException("Class creation failed", "CLASS_CREATION_ERROR")
    
    @staticmethod
    async def enroll_student(db: AsyncSession, class_id: int, student_id: int) -> bool:
        """Enroll a student in a class"""
        try:
            # Check if class exists
            class_obj = await crud.get_class_by_id(db, class_id=class_id)
            if not class_obj:
                raise SMSException("Class not found", "CLASS_NOT_FOUND")
            
            # Check if student exists
            student = await crud.get_user_by_id(db, user_id=student_id)
            if not student or student.role != "student":
                raise SMSException("Student not found", "STUDENT_NOT_FOUND")
            
            # Check if already enrolled
            existing_enrollment = await crud.get_student_class_enrollment(
                db, student_id=student_id, class_id=class_id
            )
            if existing_enrollment:
                raise SMSException("Student already enrolled in this class", "ALREADY_ENROLLED")
            
            # Create enrollment
            enrollment = await crud.create_student_class_enrollment(
                db, student_id=student_id, class_id=class_id
            )
            logger.info("Student enrolled successfully", student_id=student_id, class_id=class_id)
            return True
        except SMSException:
            raise
        except Exception as e:
            logger.error("Student enrollment failed", error=str(e))
            raise SMSException("Student enrollment failed", "ENROLLMENT_ERROR")
    
    @staticmethod
    async def unenroll_student(db: AsyncSession, class_id: int, student_id: int) -> bool:
        """Unenroll a student from a class"""
        try:
            enrollment = await crud.get_student_class_enrollment(
                db, student_id=student_id, class_id=class_id
            )
            if not enrollment:
                raise SMSException("Student not enrolled in this class", "NOT_ENROLLED")
            
            await crud.delete_student_class_enrollment(db, student_id=student_id, class_id=class_id)
            logger.info("Student unenrolled successfully", student_id=student_id, class_id=class_id)
            return True
        except SMSException:
            raise
        except Exception as e:
            logger.error("Student unenrollment failed", error=str(e))
            raise SMSException("Student unenrollment failed", "UNENROLLMENT_ERROR")
    
    @staticmethod
    async def get_class_statistics(db: AsyncSession, class_id: int) -> Dict[str, Any]:
        """Get statistics for a class"""
        try:
            stats = await crud.get_class_statistics(db, class_id=class_id)
            return stats
        except Exception as e:
            logger.error("Failed to get class statistics", error=str(e))
            raise SMSException("Failed to retrieve class statistics", "CLASS_STATS_ERROR")

class QuizService:
    """Quiz management service"""
    
    @staticmethod
    async def create_quiz(db: AsyncSession, quiz_create: schemas.QuizCreate) -> schemas.Quiz:
        """Create a new quiz"""
        try:
            # Verify class exists
            class_obj = await crud.get_class_by_id(db, class_id=quiz_create.class_id)
            if not class_obj:
                raise SMSException("Class not found", "CLASS_NOT_FOUND")
            
            quiz = await crud.create_quiz(db, quiz=quiz_create)
            logger.info("Quiz created successfully", quiz_id=quiz.id, class_id=quiz.class_id)
            return quiz
        except SMSException:
            raise
        except Exception as e:
            logger.error("Quiz creation failed", error=str(e))
            raise SMSException("Quiz creation failed", "QUIZ_CREATION_ERROR")
    
    @staticmethod
    async def add_quiz_question(
        db: AsyncSession, 
        quiz_id: int, 
        question_create: schemas.QuizQuestionCreate
    ) -> schemas.QuizQuestion:
        """Add a question to a quiz"""
        try:
            # Verify quiz exists
            quiz = await crud.get_quiz_by_id(db, quiz_id=quiz_id)
            if not quiz:
                raise SMSException("Quiz not found", "QUIZ_NOT_FOUND")
            
            question_create.quiz_id = quiz_id
            question = await crud.create_quiz_question(db, question=question_create)
            logger.info("Quiz question added", question_id=question.id, quiz_id=quiz_id)
            return question
        except SMSException:
            raise
        except Exception as e:
            logger.error("Quiz question creation failed", error=str(e))
            raise SMSException("Quiz question creation failed", "QUESTION_CREATION_ERROR")
    
    @staticmethod
    async def grade_quiz_attempt(
        db: AsyncSession, 
        attempt_id: int
    ) -> schemas.QuizAttempt:
        """Grade a quiz attempt"""
        try:
            attempt = await crud.get_quiz_attempt_by_id(db, attempt_id=attempt_id)
            if not attempt:
                raise SMSException("Quiz attempt not found", "ATTEMPT_NOT_FOUND")
            
            # Get quiz questions
            questions = await crud.get_quiz_questions(db, quiz_id=attempt.quiz_id)
            
            # Calculate score
            correct_answers = 0
            total_questions = len(questions)
            
            if total_questions > 0:
                # Simple scoring logic - this could be enhanced
                for question in questions:
                    if question.correct_answer in attempt.answers:
                        correct_answers += 1
                
                score = (correct_answers / total_questions) * 100
                
                # Update attempt with score
                await crud.update_quiz_attempt_score(db, attempt_id=attempt_id, score=score)
                attempt.score = score
            
            logger.info("Quiz attempt graded", attempt_id=attempt_id, score=score)
            return attempt
        except SMSException:
            raise
        except Exception as e:
            logger.error("Quiz grading failed", error=str(e))
            raise SMSException("Quiz grading failed", "GRADING_ERROR")

class AttendanceService:
    """Attendance management service"""
    
    @staticmethod
    async def record_attendance(
        db: AsyncSession, 
        attendance_create: schemas.AttendanceCreate
    ) -> schemas.AttendanceRecord:
        """Record attendance for a student"""
        try:
            # Check if attendance already recorded for this date
            existing_record = await crud.get_attendance_by_date(
                db, 
                student_id=attendance_create.student_id,
                class_id=attendance_create.class_id,
                date=attendance_create.date
            )
            
            if existing_record:
                # Update existing record
                attendance = await crud.update_attendance(
                    db, 
                    attendance_id=existing_record.id,
                    attendance_update=attendance_create
                )
                logger.info("Attendance updated", attendance_id=attendance.id)
            else:
                # Create new record
                attendance = await crud.create_attendance(db, attendance=attendance_create)
                logger.info("Attendance recorded", attendance_id=attendance.id)
            
            return attendance
        except Exception as e:
            logger.error("Attendance recording failed", error=str(e))
            raise SMSException("Attendance recording failed", "ATTENDANCE_ERROR")
    
    @staticmethod
    async def get_attendance_summary(
        db: AsyncSession, 
        student_id: int, 
        class_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get attendance summary for a student"""
        try:
            summary = await crud.get_attendance_summary(
                db,
                student_id=student_id,
                class_id=class_id,
                start_date=start_date,
                end_date=end_date
            )
            return summary
        except Exception as e:
            logger.error("Failed to get attendance summary", error=str(e))
            raise SMSException("Failed to retrieve attendance summary", "ATTENDANCE_SUMMARY_ERROR")
    
    @staticmethod
    async def get_class_attendance_report(
        db: AsyncSession, 
        class_id: int, 
        date: date
    ) -> List[Dict[str, Any]]:
        """Get attendance report for a class on a specific date"""
        try:
            report = await crud.get_class_attendance_report(db, class_id=class_id, date=date)
            return report
        except Exception as e:
            logger.error("Failed to get class attendance report", error=str(e))
            raise SMSException("Failed to retrieve attendance report", "ATTENDANCE_REPORT_ERROR")

class ReportService:
    """Reporting and analytics service"""
    
    @staticmethod
    async def generate_student_performance_report(
        db: AsyncSession, 
        student_id: int
    ) -> Dict[str, Any]:
        """Generate comprehensive performance report for a student"""
        try:
            # Get student info
            student = await crud.get_user_by_id(db, user_id=student_id)
            if not student:
                raise SMSException("Student not found", "STUDENT_NOT_FOUND")
            
            # Get attendance summary
            attendance = await crud.get_student_attendance_summary(db, student_id=student_id)
            
            # Get quiz performance
            quiz_performance = await crud.get_student_quiz_performance(db, student_id=student_id)
            
            # Get class enrollment
            classes = await crud.get_student_classes(db, student_id=student_id)
            
            report = {
                "student_info": {
                    "id": student.id,
                    "name": f"{student.first_name} {student.last_name}",
                    "email": student.email
                },
                "attendance": attendance,
                "quiz_performance": quiz_performance,
                "classes": classes,
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
    async def generate_class_analytics(
        db: AsyncSession, 
        class_id: int
    ) -> Dict[str, Any]:
        """Generate analytics for a class"""
        try:
            # Get class info
            class_obj = await crud.get_class_by_id(db, class_id=class_id)
            if not class_obj:
                raise SMSException("Class not found", "CLASS_NOT_FOUND")
            
            # Get enrolled students count
            students = await crud.get_class_students(db, class_id=class_id)
            
            # Get quiz statistics
            quiz_stats = await crud.get_class_quiz_statistics(db, class_id=class_id)
            
            # Get attendance statistics
            attendance_stats = await crud.get_class_attendance_statistics(db, class_id=class_id)
            
            analytics = {
                "class_info": {
                    "id": class_obj.id,
                    "name": class_obj.name,
                    "description": class_obj.description
                },
                "enrollment": {
                    "total_students": len(students),
                    "students": students
                },
                "quiz_statistics": quiz_stats,
                "attendance_statistics": attendance_stats,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info("Class analytics generated", class_id=class_id)
            return analytics
        except SMSException:
            raise
        except Exception as e:
            logger.error("Failed to generate class analytics", error=str(e))
            raise SMSException("Analytics generation failed", "ANALYTICS_ERROR")
