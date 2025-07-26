from sqlalchemy import Column, String, Boolean, DateTime, Integer, Numeric, Date, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref

# Import models for column references in foreign_keys
import typing
if typing.TYPE_CHECKING:
    from app.db.models import StudentClass, GuardianStudent, QuizAttempt, AttendanceRecord, Tenant
from sqlalchemy.sql import func
from uuid import uuid4
from datetime import datetime
from enum import Enum

from app.db.database import Base


class UserRole(str, Enum):
    """User role enumeration."""
    OWNER = "owner"
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    GUARDIAN = "guardian"


class QuizStatus(str, Enum):
    """Quiz status enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class AttendanceStatus(str, Enum):
    """Attendance status enumeration."""
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"


class AttemptStatus(str, Enum):
    """Quiz attempt status enumeration."""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class User(Base):
    """User model for all system users."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    phone_number = Column(String(20))
    role = Column(String(20), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    # If a tenant is deleted, set tenant_id to NULL for users
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Relationships - FIX: Specify foreign_keys to resolve ambiguity
    taught_classes = relationship("Class", back_populates="teacher")
    student_classes = relationship("StudentClass", back_populates="student")
    # Relationships that require foreign_keys are assigned after all classes are defined
    created_quizzes = relationship("Quiz", back_populates="creator")
    guardian_students = relationship("GuardianStudent", back_populates="guardian", foreign_keys='GuardianStudent.guardian_id')
    quiz_attempts = relationship("QuizAttempt", back_populates="student")
    attendance_records = relationship("AttendanceRecord", back_populates="student", foreign_keys='AttendanceRecord.student_id')
    
    @property
    def full_name(self) -> str:
        """Return full name."""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<User(email='{self.email}', role='{self.role}')>"


class Class(Base):
    """Class model for managing school classes."""
    __tablename__ = "classes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subject = Column(String(100), nullable=False)
    academic_year = Column(String(20), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    teacher = relationship("User", back_populates="taught_classes")
    student_classes = relationship("StudentClass", back_populates="class_")
    quizzes = relationship("Quiz", back_populates="class_")
    attendance_records = relationship("AttendanceRecord", back_populates="class_")
    
    def __repr__(self):
        return f"<Class(name='{self.name}', subject='{self.subject}')>"


class StudentClass(Base):
    """Many-to-many relationship between students and classes."""
    __tablename__ = "student_classes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    student = relationship("User", back_populates="student_classes")
    class_ = relationship("Class", back_populates="student_classes")
    
    def __repr__(self):
        return f"<StudentClass(student_id='{self.student_id}', class_id='{self.class_id}')>"


class GuardianStudent(Base):
    """Relationship between guardians and students."""
    __tablename__ = "guardian_students"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    guardian_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    relationship_type = Column(String(50), nullable=False)  # parent, guardian, etc.
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    guardian = relationship("User", back_populates="guardian_students", foreign_keys=[guardian_id])
    student = relationship("User", foreign_keys=[student_id])
    
    def __repr__(self):
        return f"<GuardianStudent(guardian_id='{self.guardian_id}', student_id='{self.student_id}')>"


class Quiz(Base):
    """Quiz model for managing quizzes."""
    __tablename__ = "quizzes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    time_limit_minutes = Column(Integer, default=30)
    max_attempts = Column(Integer, default=3)
    passing_score = Column(Numeric(5, 2), default=70.0)
    is_published = Column(Boolean, default=False)
    status = Column(String(20), default=QuizStatus.DRAFT)
    scheduled_start = Column(DateTime(timezone=True))
    scheduled_end = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    class_ = relationship("Class", back_populates="quizzes")
    creator = relationship("User", back_populates="created_quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz")
    
    def __repr__(self):
        return f"<Quiz(title='{self.title}', status='{self.status}')>"


class QuizQuestion(Base):
    """Quiz question model."""
    __tablename__ = "quiz_questions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20), nullable=False)  # multiple_choice, true_false, short_answer
    options = Column(JSON)  # For multiple choice questions
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text)
    points = Column(Integer, default=1)
    order_number = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    
    def __repr__(self):
        return f"<QuizQuestion(quiz_id='{self.quiz_id}', type='{self.question_type}')>"


class QuizAttempt(Base):
    """Quiz attempt model for tracking student quiz attempts."""
    __tablename__ = "quiz_attempts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    answers = Column(JSON)  # Student answers
    score = Column(Numeric(5, 2))
    percentage = Column(Numeric(5, 2))
    time_taken_minutes = Column(Integer)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    status = Column(String(20), default=AttemptStatus.IN_PROGRESS)
    attempt_number = Column(Integer, default=1)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    student = relationship("User", back_populates="quiz_attempts")
    
    def __repr__(self):
        return f"<QuizAttempt(quiz_id='{self.quiz_id}', student_id='{self.student_id}', status='{self.status}')>"


class AttendanceRecord(Base):
    """Attendance record model."""
    __tablename__ = "attendance_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False)
    notes = Column(Text)
    recorded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("User", back_populates="attendance_records", foreign_keys=[student_id])
    class_ = relationship("Class", back_populates="attendance_records")
    recorder = relationship("User", foreign_keys=[recorded_by])
    
    def __repr__(self):
        return f"<AttendanceRecord(student_id='{self.student_id}', date='{self.date}', status='{self.status}')>"


class Tenant(Base):
    """Tenant model for multi-tenant SaaS (organization or solo teacher)."""
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    is_organization = Column(Boolean, default=True)  # True for org, False for solo teacher
    # A tenant must always have an owner after creation (enforced in business logic)
    owner_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships that require foreign_keys are assigned after all classes are defined

    def __repr__(self):
        return f"<Tenant(name='{self.name}', is_organization={self.is_organization})>"