from sqlalchemy import Column, String, Boolean, DateTime, Integer, Numeric, Date, Text, ForeignKey, JSON, ARRAY
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from uuid import uuid4
from datetime import datetime
from enum import Enum

from app.db.database import Base


class UserStatus(str, Enum):
    """User status enumeration."""
    ONLINE = "online"
    OFFLINE = "offline"
    AWAY = "away"


class QuizStatus(str, Enum):
    """Quiz status enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class AttemptStatus(str, Enum):
    """Quiz attempt status enumeration."""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    PAUSED = "paused"


class EnrollmentStatus(str, Enum):
    """Enrollment status enumeration."""
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"


class GuardianStatus(str, Enum):
    """Guardian-child relationship status."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class EnrollmentSource(str, Enum):
    """Source of student enrollment."""
    SELF_ENROLL = "self_enroll"
    INVITE = "invite"
    ADMIN_ADD = "admin_add"


class RelationshipType(str, Enum):
    """Guardian-child relationship types."""
    PARENT = "parent"
    GUARDIAN = "guardian"
    SIBLING = "sibling"
    CAREGIVER = "caregiver"


class QuestionType(str, Enum):
    """Question types for question bank."""
    MCQ = "mcq"
    ESSAY = "essay"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"


# ---------- LOOKUPS ----------
class Role(Base):
    """Role lookup table."""
    __tablename__ = "roles"
    
    role = Column(String(50), primary_key=True)  # org_owner, org_teacher, org_admin, solo_teacher, student, guardian


# ---------- CORE USERS ----------
class User(Base):
    """User model for all system users."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), nullable=False, unique=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    # Generated column equivalent - computed property
    phone_number = Column(String(20), unique=True)  # E.164 format
    avatar_url = Column(String(500))
    locale = Column(String(10), default='en-GB')
    last_login_at = Column(DateTime(timezone=True))
    status = Column(String(20), default=UserStatus.OFFLINE)
    # Remove password_hash if using Supabase Auth, or keep if using manual auth
    # password_hash = Column(String(255), nullable=False)  # Commented out for Supabase
    is_active = Column(Boolean, default=True)  # Added for user management
    is_verified = Column(Boolean, default=False)  # Added for email verification
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    owned_organizations = relationship("Organization", back_populates="owner", foreign_keys="Organization.owner_user_id")
    student_profile = relationship("StudentProfile", back_populates="student", uselist=False)
    taught_courses = relationship("TeacherCourse", back_populates="teacher")
    admin_course_rights = relationship("OrgAdminCourseRight", back_populates="admin")
    quiz_attempts = relationship("QuizAttempt", back_populates="student")
    guardian_children = relationship("GuardianChild", back_populates="guardian", foreign_keys="GuardianChild.guardian_id")
    child_guardians = relationship("GuardianChild", back_populates="child", foreign_keys="GuardianChild.student_id")
    student_enrollments = relationship("StudentEnrollment", back_populates="student")
    
    @property
    def full_name(self) -> str:
        """Return full name."""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<User(email='{self.email}')>"


class UserRole(Base):
    """User role assignments."""
    __tablename__ = "user_roles"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role = Column(String(50), ForeignKey("roles.role"), primary_key=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"))  # nullable
    solo_teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # nullable
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="user_roles")
    role_obj = relationship("Role")
    organization = relationship("Organization", foreign_keys=[organization_id])
    solo_teacher = relationship("User", foreign_keys=[solo_teacher_id])


# ---------- PROVIDERS ----------
class Organization(Base):
    """Organization model for multi-tenant support."""
    __tablename__ = "organization"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(200), nullable=False)
    owner_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="owned_organizations", foreign_keys=[owner_user_id])
    courses = relationship("Course", back_populates="organization")
    question_bank_questions = relationship("QuestionBank", back_populates="organization")
    student_profiles = relationship("StudentProfile", back_populates="organization")
    
    def __repr__(self):
        return f"<Organization(name='{self.name}')>"


class StudentProfile(Base):
    """Student profile for linking students to providers."""
    __tablename__ = "student_profiles"
    
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"))  # nullable
    solo_teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # nullable
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    student = relationship("User", back_populates="student_profile")
    organization = relationship("Organization", back_populates="student_profiles")
    solo_teacher = relationship("User", foreign_keys=[solo_teacher_id])


# ---------- COURSES & TEACHING ----------
class Course(Base):
    """Course model."""
    __tablename__ = "course"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"), nullable=False)
    title = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="courses")
    teacher_courses = relationship("TeacherCourse", back_populates="course")
    admin_course_rights = relationship("OrgAdminCourseRight", back_populates="course")
    quizzes = relationship("Quiz", back_populates="course")
    student_enrollments = relationship("StudentEnrollment", back_populates="course")
    
    def __repr__(self):
        return f"<Course(title='{self.title}')>"


class TeacherCourse(Base):
    """N:M teacher ⇄ course relationship."""
    __tablename__ = "teacher_courses"
    
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey("course.id"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    teacher = relationship("User", back_populates="taught_courses")
    course = relationship("Course", back_populates="teacher_courses")


class OrgAdminCourseRight(Base):
    """N:M admin ⇄ course relationship."""
    __tablename__ = "org_admin_course_rights"
    
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey("course.id"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    admin = relationship("User", back_populates="admin_course_rights")
    course = relationship("Course", back_populates="admin_course_rights")


# ---------- QUIZZES ----------
class Quiz(Base):
    """Quiz model."""
    __tablename__ = "quiz"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("course.id"), nullable=False)
    title = Column(String(200))
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    course = relationship("Course", back_populates="quizzes")
    quiz_questions = relationship("QuizQuestion", back_populates="quiz")
    quiz_attempts = relationship("QuizAttempt", back_populates="quiz")
    
    def __repr__(self):
        return f"<Quiz(title='{self.title}')>"


# ---------- QUESTION BANK ----------
class QuestionBank(Base):
    """Question bank for reusable questions."""
    __tablename__ = "question_bank"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Provider (one non-NULL)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"))  # nullable
    solo_teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # nullable
    
    # Core content
    text = Column(Text, nullable=False)  # prompt/stem
    qtype = Column(String(20), nullable=False)  # mcq, essay, true_false, short_answer
    explanation = Column(Text)  # feedback for students
    
    # Multiple-choice specific
    options = Column(ARRAY(Text))  # MCQ choices (NULL unless qtype = mcq)
    correct_answer = Column(Integer)  # index into options[] (NULL if not MCQ)
    
    # Essay/long-form specific
    word_limit = Column(Integer)  # e.g. 250; NULL for non-essay
    rubric = Column(JSONB, default={})  # optional grading rubric
    
    # Common metadata
    difficulty = Column(String(20), default='dok1')
    points = Column(Integer, default=1)
    time_limit = Column(Integer)  # per-question seconds
    tags = Column(ARRAY(Text))
    media = Column(JSONB, default={})  # {imageUrl, videoUrl, ...}
    meta = Column(JSONB, default={})  # extensible flags
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="question_bank_questions")
    solo_teacher = relationship("User", foreign_keys=[solo_teacher_id])
    quiz_questions = relationship("QuizQuestion", back_populates="question")
    
    def __repr__(self):
        return f"<QuestionBank(qtype='{self.qtype}')>"


# ---------- QUIZ ⇄ QUESTION LINK ----------
class QuizQuestion(Base):
    """Link between quizzes and questions."""
    __tablename__ = "quiz_questions"
    
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quiz.id"), primary_key=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("question_bank.id"), primary_key=True)
    
    position = Column(Integer)  # display order
    points = Column(Integer, default=1)  # override per quiz
    randomize = Column(Boolean, default=False)  # ignore "position" when true
    show_explanation = Column(Boolean, default=True)  # per-quiz toggle
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="quiz_questions")
    question = relationship("QuestionBank", back_populates="quiz_questions")


# ---------- QUIZ ATTEMPTS ----------
class QuizAttempt(Base):
    """Quiz attempt tracking."""
    __tablename__ = "quiz_attempts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quiz.id"))
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    finished_at = Column(DateTime(timezone=True))
    time_spent = Column(Integer)  # seconds
    
    # Results
    status = Column(String(20), default=AttemptStatus.IN_PROGRESS, nullable=False)
    score = Column(Numeric)  # raw points
    percentage = Column(Numeric(5,2))  # (score / max)*100
    
    # Analytics/security
    answers = Column(JSONB, default=[])  # [{qId, selected, correct, timeSpent}…]
    questions_seen = Column(ARRAY(Text))  # for adaptive/anti-repeat
    security_violations = Column(JSONB, default=[])  # [{type, ts, details}…]
    device_info = Column(JSONB)  # {device, os, browser, screen}
    ip_address = Column(INET)
    flagged_for_review = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="quiz_attempts")
    student = relationship("User", back_populates="quiz_attempts")
    
    def __repr__(self):
        return f"<QuizAttempt(quiz_id='{self.quiz_id}', student_id='{self.student_id}', status='{self.status}')>"


# ---------- GUARDIAN ⇄ CHILD ----------
class GuardianChild(Base):
    """N:M guardian ↔ student relationship."""
    __tablename__ = "guardian_children"
    
    guardian_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    
    relationship = Column(String(50), default='parent', nullable=False)  # parent, guardian, sibling, caregiver
    nickname = Column(String(100))  # "Mum", "Dad", "Big Sis"
    avatar_url = Column(String(500))
    status = Column(String(20), default=GuardianStatus.PENDING, nullable=False)  # pending, accepted, rejected
    verified_at = Column(DateTime(timezone=True))  # when OTP completed
    last_sync_at = Column(DateTime(timezone=True))  # last parent login while acting for this child
    communication_prefs = Column(JSONB, default={})  # email/sms flags
    preferences = Column(JSONB, default={})  # UI theme, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    guardian = relationship("User", back_populates="guardian_children", foreign_keys=[guardian_id])
    child = relationship("User", back_populates="child_guardians", foreign_keys=[student_id])
    
    def __repr__(self):
        return f"<GuardianChild(guardian_id='{self.guardian_id}', student_id='{self.student_id}')>"


# ---------- STUDENT ⇄ COURSE ENROLLMENTS ----------
class StudentEnrollment(Base):
    """N:M student ↔ course relationship."""
    __tablename__ = "student_enrolments"
    
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey("course.id"), primary_key=True)
    
    status = Column(String(20), default=EnrollmentStatus.ACTIVE, nullable=False)  # active, completed, dropped
    role = Column(String(20), default='student')  # student, observer, assistant
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True))  # filled when status = completed
    grade = Column(Numeric(5,2))  # final score %
    progress = Column(JSONB, default={})  # cached stats (attempts, avg score…)
    source = Column(String(20), default='admin_add')  # self_enroll, invite, admin_add
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    student = relationship("User", back_populates="student_enrollments")
    course = relationship("Course", back_populates="student_enrollments")
    
    def __repr__(self):
        return f"<StudentEnrollment(student_id='{self.student_id}', course_id='{self.course_id}')>"