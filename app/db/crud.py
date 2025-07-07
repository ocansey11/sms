from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, delete
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date
import structlog

from app.db.models import (
    User, Class, StudentClass, GuardianStudent,
    Quiz, QuizQuestion, QuizAttempt, AttendanceRecord,
    UserRole, QuizStatus, AttemptStatus, AttendanceStatus
)
from app.db.schemas import (
    UserCreate, UserUpdate, ClassCreate, ClassUpdate,
    QuizCreate, QuizUpdate, QuizQuestionCreate, QuizQuestionUpdate,
    QuizAttemptCreate, QuizAttemptUpdate, AttendanceCreate, AttendanceUpdate
)
from app.core.security import security
from app.exceptions.custom_exceptions import (
    UserNotFoundException, UserAlreadyExistsException,
    ClassNotFoundException, QuizNotFoundException,
    StudentNotEnrolledException, ConflictException
)

logger = structlog.get_logger()


class CRUDBase:
    """Base CRUD class with common operations."""
    
    def __init__(self, model):
        self.model = model
    
    async def get(self, db: AsyncSession, id: UUID) -> Optional[Any]:
        """Get a single record by ID."""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        **filters
    ) -> List[Any]:
        """Get multiple records with pagination and filters."""
        query = select(self.model)
        
        # Apply filters
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.where(getattr(self.model, key) == value)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def count(self, db: AsyncSession, **filters) -> int:
        """Count records with filters."""
        query = select(func.count(self.model.id))
        
        # Apply filters
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.where(getattr(self.model, key) == value)
        
        result = await db.execute(query)
        return result.scalar()
    
    async def create(self, db: AsyncSession, *, obj_in: Dict[str, Any]) -> Any:
        """Create a new record."""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: Any, 
        obj_in: Dict[str, Any]
    ) -> Any:
        """Update an existing record."""
        for field, value in obj_in.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, *, id: UUID) -> Any:
        """Delete a record by ID."""
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj


class CRUDUser(CRUDBase):
    """CRUD operations for User model."""
    
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = await self.get_by_email(db, email=obj_in.email)
        if existing_user:
            raise UserAlreadyExistsException(obj_in.email)
        
        # Hash password
        hashed_password = security.get_password_hash(obj_in.password)
        
        # Create user data
        user_data = obj_in.model_dump(exclude={'password'})
        user_data['password_hash'] = hashed_password
        
        return await super().create(db, obj_in=user_data)
    
    async def update(self, db: AsyncSession, *, db_obj: User, obj_in: UserUpdate) -> User:
        """Update user."""
        update_data = obj_in.model_dump(exclude_unset=True)
        return await super().update(db, db_obj=db_obj, obj_in=update_data)
    
    async def authenticate(self, db: AsyncSession, *, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not security.verify_password(password, user.password_hash):
            return None
        return user
    
    async def get_by_role(self, db: AsyncSession, *, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by role."""
        return await self.get_multi(db, skip=skip, limit=limit, role=role)


class CRUDClass(CRUDBase):
    """CRUD operations for Class model."""
    
    async def get_with_teacher(self, db: AsyncSession, id: UUID) -> Optional[Class]:
        """Get class with teacher information."""
        result = await db.execute(
            select(Class)
            .options(selectinload(Class.teacher))
            .where(Class.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_teacher(self, db: AsyncSession, *, teacher_id: UUID, skip: int = 0, limit: int = 100) -> List[Class]:
        """Get classes by teacher."""
        return await self.get_multi(db, skip=skip, limit=limit, teacher_id=teacher_id, is_active=True)
    
    async def create(self, db: AsyncSession, *, obj_in: ClassCreate) -> Class:
        """Create a new class."""
        class_data = obj_in.model_dump()
        return await super().create(db, obj_in=class_data)
    
    async def enroll_student(self, db: AsyncSession, *, class_id: UUID, student_id: UUID) -> StudentClass:
        """Enroll a student in a class."""
        # Check if already enrolled
        existing = await db.execute(
            select(StudentClass).where(
                and_(
                    StudentClass.class_id == class_id,
                    StudentClass.student_id == student_id,
                    StudentClass.is_active == True
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictException("Student is already enrolled in this class")
        
        enrollment = StudentClass(class_id=class_id, student_id=student_id)
        db.add(enrollment)
        await db.commit()
        await db.refresh(enrollment)
        return enrollment
    
    async def get_enrolled_students(self, db: AsyncSession, *, class_id: UUID) -> List[User]:
        """Get students enrolled in a class."""
        result = await db.execute(
            select(User)
            .join(StudentClass, User.id == StudentClass.student_id)
            .where(
                and_(
                    StudentClass.class_id == class_id,
                    StudentClass.is_active == True
                )
            )
        )
        return result.scalars().all()


class CRUDQuiz(CRUDBase):
    """CRUD operations for Quiz model."""
    
    async def get_with_questions(self, db: AsyncSession, id: UUID) -> Optional[Quiz]:
        """Get quiz with questions."""
        result = await db.execute(
            select(Quiz)
            .options(selectinload(Quiz.questions))
            .where(Quiz.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_class(self, db: AsyncSession, *, class_id: UUID, skip: int = 0, limit: int = 100) -> List[Quiz]:
        """Get quizzes by class."""
        return await self.get_multi(db, skip=skip, limit=limit, class_id=class_id)
    
    async def get_published_by_class(self, db: AsyncSession, *, class_id: UUID) -> List[Quiz]:
        """Get published quizzes by class."""
        result = await db.execute(
            select(Quiz).where(
                and_(
                    Quiz.class_id == class_id,
                    Quiz.is_published == True,
                    Quiz.status == QuizStatus.PUBLISHED
                )
            )
        )
        return result.scalars().all()
    
    async def create(self, db: AsyncSession, *, obj_in: QuizCreate, creator_id: UUID) -> Quiz:
        """Create a new quiz."""
        quiz_data = obj_in.model_dump()
        quiz_data['created_by'] = creator_id
        return await super().create(db, obj_in=quiz_data)


class CRUDQuizQuestion(CRUDBase):
    """CRUD operations for QuizQuestion model."""
    
    async def get_by_quiz(self, db: AsyncSession, *, quiz_id: UUID) -> List[QuizQuestion]:
        """Get questions by quiz."""
        result = await db.execute(
            select(QuizQuestion)
            .where(QuizQuestion.quiz_id == quiz_id)
            .order_by(QuizQuestion.order_number)
        )
        return result.scalars().all()
    
    async def create(self, db: AsyncSession, *, obj_in: QuizQuestionCreate) -> QuizQuestion:
        """Create a new quiz question."""
        question_data = obj_in.model_dump()
        return await super().create(db, obj_in=question_data)


class CRUDQuizAttempt(CRUDBase):
    """CRUD operations for QuizAttempt model."""
    
    async def get_by_student_and_quiz(
        self, 
        db: AsyncSession, 
        *, 
        student_id: UUID, 
        quiz_id: UUID
    ) -> List[QuizAttempt]:
        """Get attempts by student and quiz."""
        result = await db.execute(
            select(QuizAttempt)
            .where(
                and_(
                    QuizAttempt.student_id == student_id,
                    QuizAttempt.quiz_id == quiz_id
                )
            )
            .order_by(desc(QuizAttempt.started_at))
        )
        return result.scalars().all()
    
    async def get_active_attempt(
        self, 
        db: AsyncSession, 
        *, 
        student_id: UUID, 
        quiz_id: UUID
    ) -> Optional[QuizAttempt]:
        """Get active (in-progress) attempt."""
        result = await db.execute(
            select(QuizAttempt).where(
                and_(
                    QuizAttempt.student_id == student_id,
                    QuizAttempt.quiz_id == quiz_id,
                    QuizAttempt.status == AttemptStatus.IN_PROGRESS
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, *, obj_in: QuizAttemptCreate, student_id: UUID) -> QuizAttempt:
        """Create a new quiz attempt."""
        # Get attempt number
        existing_attempts = await self.get_by_student_and_quiz(
            db, student_id=student_id, quiz_id=obj_in.quiz_id
        )
        attempt_number = len(existing_attempts) + 1
        
        attempt_data = obj_in.model_dump()
        attempt_data['student_id'] = student_id
        attempt_data['attempt_number'] = attempt_number
        
        return await super().create(db, obj_in=attempt_data)


class CRUDAttendance(CRUDBase):
    """CRUD operations for AttendanceRecord model."""
    
    async def get_by_student_and_date_range(
        self,
        db: AsyncSession,
        *,
        student_id: UUID,
        start_date: str,
        end_date: str
    ) -> List[AttendanceRecord]:
        """Get attendance records for a student in date range."""
        result = await db.execute(
            select(AttendanceRecord)
            .where(
                and_(
                    AttendanceRecord.student_id == student_id,
                    AttendanceRecord.date >= start_date,
                    AttendanceRecord.date <= end_date
                )
            )
            .order_by(desc(AttendanceRecord.date))
        )
        return result.scalars().all()
    
    async def get_by_class_and_date(
        self,
        db: AsyncSession,
        *,
        class_id: UUID,
        date: str
    ) -> List[AttendanceRecord]:
        """Get attendance records for a class on specific date."""
        result = await db.execute(
            select(AttendanceRecord)
            .options(selectinload(AttendanceRecord.student))
            .where(
                and_(
                    AttendanceRecord.class_id == class_id,
                    AttendanceRecord.date == date
                )
            )
        )
        return result.scalars().all()
    
    async def create(self, db: AsyncSession, *, obj_in: AttendanceCreate, recorded_by: UUID) -> AttendanceRecord:
        """Create attendance record."""
        attendance_data = obj_in.model_dump()
        attendance_data['recorded_by'] = recorded_by
        return await super().create(db, obj_in=attendance_data)


# Create CRUD instances
user = CRUDUser(User)
class_ = CRUDClass(Class)
quiz = CRUDQuiz(Quiz)
quiz_question = CRUDQuizQuestion(QuizQuestion)
quiz_attempt = CRUDQuizAttempt(QuizAttempt)
attendance = CRUDAttendance(AttendanceRecord)

# Additional convenience functions for API routes
async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email - convenience function"""
    return await user.get_by_email(db, email=email)

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID - convenience function"""
    return await user.get(db, id=user_id)

async def get_users_by_role(db: AsyncSession, role: str, skip: int = 0, limit: int = 100) -> List[User]:
    """Get users by role - convenience function"""
    return await user.get_by_role(db, role=UserRole(role), skip=skip, limit=limit)

async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """Create user - convenience function"""
    return await user.create(db, obj_in=user)

async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate) -> User:
    """Update user - convenience function"""
    db_user = await user.get(db, id=user_id)
    return await user.update(db, db_obj=db_user, obj_in=user_update)

async def update_user_password(db: AsyncSession, user_id: int, hashed_password: str) -> bool:
    """Update user password"""
    db_user = await user.get(db, id=user_id)
    if db_user:
        db_user.hashed_password = hashed_password
        db.add(db_user)
        await db.commit()
        return True
    return False

async def deactivate_user(db: AsyncSession, user_id: int) -> bool:
    """Deactivate user account"""
    db_user = await user.get(db, id=user_id)
    if db_user:
        db_user.is_active = False
        db.add(db_user)
        await db.commit()
        return True
    return False

async def get_user_statistics(db: AsyncSession) -> dict:
    """Get user statistics"""
    try:
        total_users = await db.scalar(select(func.count(User.id)))
        active_users = await db.scalar(select(func.count(User.id)).where(User.is_active == True))
        
        role_counts = await db.execute(
            select(User.role, func.count(User.id)).group_by(User.role)
        )
        
        return {
            "total_users": total_users or 0,
            "active_users": active_users or 0,
            "role_distribution": {role: count for role, count in role_counts}
        }
    except Exception:
        return {"total_users": 0, "active_users": 0, "role_distribution": {}}

# Class-related convenience functions
async def get_class_by_id(db: AsyncSession, class_id: int) -> Optional[Class]:
    """Get class by ID"""
    return await class_.get(db, id=class_id)

async def get_class_by_name(db: AsyncSession, name: str) -> Optional[Class]:
    """Get class by name"""
    result = await db.execute(select(Class).where(Class.name == name))
    return result.scalar_one_or_none()

async def create_class(db: AsyncSession, class_create: ClassCreate) -> Class:
    """Create class"""
    return await class_.create(db, obj_in=class_create)

async def get_student_classes(db: AsyncSession, student_id: int) -> List[Class]:
    """Get all classes for a student"""
    result = await db.execute(
        select(Class)
        .join(StudentClass)
        .where(StudentClass.student_id == student_id)
    )
    return result.scalars().all()

async def get_student_class_enrollment(db: AsyncSession, student_id: int, class_id: int) -> Optional[StudentClass]:
    """Get student class enrollment"""
    result = await db.execute(
        select(StudentClass)
        .where(StudentClass.student_id == student_id, StudentClass.class_id == class_id)
    )
    return result.scalar_one_or_none()

async def create_student_class_enrollment(db: AsyncSession, student_id: int, class_id: int) -> StudentClass:
    """Create student class enrollment"""
    enrollment = StudentClass(student_id=student_id, class_id=class_id)
    db.add(enrollment)
    await db.commit()
    await db.refresh(enrollment)
    return enrollment

async def delete_student_class_enrollment(db: AsyncSession, student_id: int, class_id: int) -> bool:
    """Delete student class enrollment"""
    result = await db.execute(
        delete(StudentClass)
        .where(StudentClass.student_id == student_id, StudentClass.class_id == class_id)
    )
    await db.commit()
    return result.rowcount > 0

async def get_class_students(db: AsyncSession, class_id: int) -> List[User]:
    """Get all students in a class"""
    result = await db.execute(
        select(User)
        .join(StudentClass)
        .where(StudentClass.class_id == class_id)
    )
    return result.scalars().all()

async def get_class_statistics(db: AsyncSession, class_id: int) -> dict:
    """Get class statistics"""
    try:
        student_count = await db.scalar(
            select(func.count(StudentClass.student_id))
            .where(StudentClass.class_id == class_id)
        )
        
        quiz_count = await db.scalar(
            select(func.count(Quiz.id))
            .where(Quiz.class_id == class_id)
        )
        
        return {
            "student_count": student_count or 0,
            "quiz_count": quiz_count or 0
        }
    except Exception:
        return {"student_count": 0, "quiz_count": 0}

# Quiz-related convenience functions
async def get_quiz_by_id(db: AsyncSession, quiz_id: int) -> Optional[Quiz]:
    """Get quiz by ID"""
    return await quiz.get(db, id=quiz_id)

async def create_quiz(db: AsyncSession, quiz: QuizCreate) -> Quiz:
    """Create quiz"""
    return await quiz.create(db, obj_in=quiz)

async def get_quiz_questions(db: AsyncSession, quiz_id: int) -> List[QuizQuestion]:
    """Get quiz questions"""
    return await quiz_question.get_by_quiz(db, quiz_id=quiz_id)

async def create_quiz_question(db: AsyncSession, question: QuizQuestionCreate) -> QuizQuestion:
    """Create quiz question"""
    return await quiz_question.create(db, obj_in=question)

async def get_student_quizzes(db: AsyncSession, student_id: int, class_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Quiz]:
    """Get quizzes available to a student"""
    query = select(Quiz).join(Class).join(StudentClass).where(StudentClass.student_id == student_id)
    
    if class_id:
        query = query.where(Quiz.class_id == class_id)
    
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

async def create_quiz_attempt(db: AsyncSession, attempt: QuizAttemptCreate) -> QuizAttempt:
    """Create quiz attempt"""
    return await quiz_attempt.create(db, obj_in=attempt)

async def get_quiz_attempt_by_id(db: AsyncSession, attempt_id: int) -> Optional[QuizAttempt]:
    """Get quiz attempt by ID"""
    return await quiz_attempt.get(db, id=attempt_id)

async def get_student_quiz_attempts(db: AsyncSession, student_id: int, quiz_id: Optional[int] = None, class_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[QuizAttempt]:
    """Get quiz attempts for a student"""
    query = select(QuizAttempt).where(QuizAttempt.student_id == student_id)
    
    if quiz_id:
        query = query.where(QuizAttempt.quiz_id == quiz_id)
    
    if class_id:
        query = query.join(Quiz).where(Quiz.class_id == class_id)
    
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

async def update_quiz_attempt_score(db: AsyncSession, attempt_id: int, score: float) -> bool:
    """Update quiz attempt score"""
    attempt = await quiz_attempt.get(db, id=attempt_id)
    if attempt:
        attempt.score = score
        db.add(attempt)
        await db.commit()
        return True
    return False

# Guardian-related functions
async def get_guardian_students(db: AsyncSession, guardian_id: int) -> List[User]:
    """Get all students under a guardian"""
    result = await db.execute(
        select(User)
        .join(GuardianStudent)
        .where(GuardianStudent.guardian_id == guardian_id)
    )
    return result.scalars().all()

async def get_guardian_student_relationship(db: AsyncSession, guardian_id: int, student_id: int) -> Optional[GuardianStudent]:
    """Get guardian-student relationship"""
    result = await db.execute(
        select(GuardianStudent)
        .where(GuardianStudent.guardian_id == guardian_id, GuardianStudent.student_id == student_id)
    )
    return result.scalar_one_or_none()

async def get_guardian_overview(db: AsyncSession, guardian_id: int) -> dict:
    """Get overview for guardian"""
    try:
        students = await get_guardian_students(db, guardian_id)
        
        overview = {
            "total_students": len(students),
            "students": [
                {
                    "id": student.id,
                    "name": f"{student.first_name} {student.last_name}",
                    "email": student.email
                }
                for student in students
            ]
        }
        
        return overview
    except Exception:
        return {"total_students": 0, "students": []}

# Attendance-related functions
async def get_student_attendance(db: AsyncSession, student_id: int, class_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[AttendanceRecord]:
    """Get student attendance records"""
    query = select(AttendanceRecord).where(AttendanceRecord.student_id == student_id)
    
    if class_id:
        query = query.where(AttendanceRecord.class_id == class_id)
    
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

async def get_student_attendance_summary(db: AsyncSession, student_id: int, class_id: Optional[int] = None) -> dict:
    """Get student attendance summary"""
    try:
        query = select(AttendanceRecord).where(AttendanceRecord.student_id == student_id)
        
        if class_id:
            query = query.where(AttendanceRecord.class_id == class_id)
        
        result = await db.execute(query)
        records = result.scalars().all()
        
        total_days = len(records)
        present_days = sum(1 for record in records if record.status == 'present')
        absent_days = total_days - present_days
        
        return {
            "total_days": total_days,
            "present_days": present_days,
            "absent_days": absent_days,
            "attendance_rate": (present_days / total_days * 100) if total_days > 0 else 0
        }
    except Exception:
        return {"total_days": 0, "present_days": 0, "absent_days": 0, "attendance_rate": 0}

async def create_attendance(db: AsyncSession, attendance: AttendanceCreate) -> AttendanceRecord:
    """Create attendance record"""
    return await attendance_record.create(db, obj_in=attendance)

async def get_attendance_by_date(db: AsyncSession, student_id: int, class_id: int, date: date) -> Optional[AttendanceRecord]:
    """Get attendance record by date"""
    result = await db.execute(
        select(AttendanceRecord)
        .where(
            AttendanceRecord.student_id == student_id,
            AttendanceRecord.class_id == class_id,
            AttendanceRecord.date == date
        )
    )
    return result.scalar_one_or_none()

async def update_attendance(db: AsyncSession, attendance_id: int, attendance_update: AttendanceUpdate) -> AttendanceRecord:
    """Update attendance record"""
    db_attendance = await attendance_record.get(db, id=attendance_id)
    return await attendance_record.update(db, db_obj=db_attendance, obj_in=attendance_update)

async def get_attendance_summary(db: AsyncSession, student_id: int, class_id: Optional[int] = None, start_date: Optional[date] = None, end_date: Optional[date] = None) -> dict:
    """Get attendance summary with date filters"""
    return await get_student_attendance_summary(db, student_id, class_id)

async def get_class_attendance_report(db: AsyncSession, class_id: int, date: date) -> List[dict]:
    """Get attendance report for a class on a specific date"""
    result = await db.execute(
        select(AttendanceRecord, User)
        .join(User, AttendanceRecord.student_id == User.id)
        .where(AttendanceRecord.class_id == class_id, AttendanceRecord.date == date)
    )
    
    return [
        {
            "student_id": record.student_id,
            "student_name": f"{user.first_name} {user.last_name}",
            "status": record.status,
            "date": record.date
        }
        for record, user in result
    ]

# Performance and grades functions
async def get_student_grades(db: AsyncSession, student_id: int, class_id: Optional[int] = None) -> List[dict]:
    """Get student grades"""
    query = select(QuizAttempt, Quiz).join(Quiz).where(QuizAttempt.student_id == student_id)
    
    if class_id:
        query = query.where(Quiz.class_id == class_id)
    
    result = await db.execute(query)
    
    grades = []
    for attempt, quiz in result:
        grades.append({
            "quiz_id": quiz.id,
            "quiz_title": quiz.title,
            "score": attempt.score,
            "max_score": quiz.max_score,
            "percentage": (attempt.score / quiz.max_score * 100) if quiz.max_score > 0 else 0,
            "submitted_at": attempt.submitted_at
        })
    
    return grades

async def get_student_performance_report(db: AsyncSession, student_id: int) -> dict:
    """Get comprehensive student performance report"""
    try:
        # Get basic info
        student = await get_user_by_id(db, student_id)
        if not student:
            return {}
        
        # Get grades
        grades = await get_student_grades(db, student_id)
        
        # Get attendance
        attendance = await get_student_attendance_summary(db, student_id)
        
        # Get classes
        classes = await get_student_classes(db, student_id)
        
        return {
            "student_info": {
                "id": student.id,
                "name": f"{student.first_name} {student.last_name}",
                "email": student.email
            },
            "grades": grades,
            "attendance": attendance,
            "classes": classes
        }
    except Exception:
        return {}

async def get_student_quiz_performance(db: AsyncSession, student_id: int) -> dict:
    """Get student quiz performance statistics"""
    try:
        attempts = await get_student_quiz_attempts(db, student_id)
        
        if not attempts:
            return {"total_attempts": 0, "average_score": 0, "best_score": 0}
        
        scores = [attempt.score for attempt in attempts if attempt.score is not None]
        
        return {
            "total_attempts": len(attempts),
            "average_score": sum(scores) / len(scores) if scores else 0,
            "best_score": max(scores) if scores else 0
        }
    except Exception:
        return {"total_attempts": 0, "average_score": 0, "best_score": 0}

async def get_class_quiz_statistics(db: AsyncSession, class_id: int) -> dict:
    """Get quiz statistics for a class"""
    try:
        quiz_count = await db.scalar(
            select(func.count(Quiz.id))
            .where(Quiz.class_id == class_id)
        )
        
        return {"total_quizzes": quiz_count or 0}
    except Exception:
        return {"total_quizzes": 0}

async def get_class_attendance_statistics(db: AsyncSession, class_id: int) -> dict:
    """Get attendance statistics for a class"""
    try:
        total_records = await db.scalar(
            select(func.count(AttendanceRecord.id))
            .where(AttendanceRecord.class_id == class_id)
        )
        
        present_records = await db.scalar(
            select(func.count(AttendanceRecord.id))
            .where(AttendanceRecord.class_id == class_id, AttendanceRecord.status == 'present')
        )
        
        return {
            "total_records": total_records or 0,
            "present_records": present_records or 0,
            "attendance_rate": (present_records / total_records * 100) if total_records > 0 else 0
        }
    except Exception:
        return {"total_records": 0, "present_records": 0, "attendance_rate": 0}
