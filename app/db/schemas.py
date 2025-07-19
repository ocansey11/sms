from pydantic import BaseModel, ConfigDict, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from enum import Enum

from app.db.models import UserRole, QuizStatus, AttendanceStatus, AttemptStatus


# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(
        from_attributes = True,
        use_enum_values = True
    )


# User schemas
class UserBase(BaseSchema):
    """Base user schema."""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone_number: Optional[str] = Field(None, max_length=20)
    role: UserRole


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseSchema):
    """Schema for updating user information."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone_number: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """Schema for user in database."""
    id: UUID
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class UserResponse(UserInDB):
    """Schema for user response (without sensitive data)."""
    pass


# Authentication schemas
class Token(BaseSchema):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: 'UserResponse'


class TokenData(BaseSchema):
    """Token data schema."""
    user_id: Optional[UUID] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None


class LoginRequest(BaseSchema):
    """Login request schema."""
    email: EmailStr
    password: str


class PasswordResetRequest(BaseSchema):
    """Password reset request schema."""
    email: EmailStr


class PasswordResetConfirm(BaseSchema):
    """Password reset confirmation schema."""
    token: str
    new_password: str = Field(..., min_length=8)


# Class schemas
class ClassBase(BaseSchema):
    """Base class schema."""
    name: str = Field(..., min_length=1, max_length=100)
    subject: str = Field(..., min_length=1, max_length=100)
    academic_year: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = None


class ClassCreate(ClassBase):
    """Schema for creating a new class."""
    teacher_id: UUID


class ClassUpdate(BaseSchema):
    """Schema for updating class information."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    subject: Optional[str] = Field(None, min_length=1, max_length=100)
    academic_year: Optional[str] = Field(None, min_length=1, max_length=20)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ClassInDB(ClassBase):
    """Schema for class in database."""
    id: UUID
    teacher_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ClassResponse(ClassInDB):
    """Schema for class response with teacher info."""
    teacher: UserResponse


# Quiz schemas
class QuizBase(BaseSchema):
    """Base quiz schema."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    time_limit_minutes: int = Field(default=30, ge=1, le=300)
    max_attempts: int = Field(default=3, ge=1, le=10)
    passing_score: float = Field(default=70.0, ge=0.0, le=100.0)


class QuizCreate(QuizBase):
    """Schema for creating a new quiz."""
    class_id: UUID


class QuizUpdate(BaseSchema):
    """Schema for updating quiz information."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    time_limit_minutes: Optional[int] = Field(None, ge=1, le=300)
    max_attempts: Optional[int] = Field(None, ge=1, le=10)
    passing_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    is_published: Optional[bool] = None
    status: Optional[QuizStatus] = None


class QuizInDB(QuizBase):
    """Schema for quiz in database."""
    id: UUID
    class_id: UUID
    created_by: UUID
    is_published: bool
    status: QuizStatus
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class QuizResponse(QuizInDB):
    """Schema for quiz response."""
    creator: UserResponse
    questions_count: Optional[int] = 0


# Quiz Question schemas
class QuizQuestionBase(BaseSchema):
    """Base quiz question schema."""
    question_text: str = Field(..., min_length=1)
    question_type: str = Field(..., pattern="^(multiple_choice|true_false|short_answer)$")
    options: Optional[List[str]] = None
    correct_answer: str = Field(..., min_length=1)
    explanation: Optional[str] = None
    points: int = Field(default=1, ge=1, le=10)


class QuizQuestionCreate(QuizQuestionBase):
    """Schema for creating a quiz question."""
    quiz_id: UUID
    order_number: int = Field(default=1, ge=1)


class QuizQuestionUpdate(BaseSchema):
    """Schema for updating quiz question."""
    question_text: Optional[str] = Field(None, min_length=1)
    question_type: Optional[str] = Field(None, pattern="^(multiple_choice|true_false|short_answer)$")
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = Field(None, min_length=1)
    explanation: Optional[str] = None
    points: Optional[int] = Field(None, ge=1, le=10)
    order_number: Optional[int] = Field(None, ge=1)


class QuizQuestionInDB(QuizQuestionBase):
    """Schema for quiz question in database."""
    id: UUID
    quiz_id: UUID
    order_number: int
    created_at: datetime
    updated_at: datetime


class QuizQuestionResponse(QuizQuestionInDB):
    """Schema for quiz question response."""
    pass


# Quiz Attempt schemas
class QuizAttemptBase(BaseSchema):
    """Base quiz attempt schema."""
    answers: Dict[str, Any] = Field(default_factory=dict)


class QuizAttemptCreate(QuizAttemptBase):
    """Schema for creating a quiz attempt."""
    quiz_id: UUID


class QuizAttemptUpdate(BaseSchema):
    """Schema for updating quiz attempt."""
    answers: Optional[Dict[str, Any]] = None
    status: Optional[AttemptStatus] = None


class QuizAttemptInDB(QuizAttemptBase):
    """Schema for quiz attempt in database."""
    id: UUID
    quiz_id: UUID
    student_id: UUID
    score: Optional[float]
    percentage: Optional[float]
    time_taken_minutes: Optional[int]
    started_at: datetime
    completed_at: Optional[datetime]
    status: AttemptStatus
    attempt_number: int


class QuizAttemptResponse(QuizAttemptInDB):
    """Schema for quiz attempt response."""
    quiz: QuizResponse
    student: UserResponse


# Attendance schemas
class AttendanceBase(BaseSchema):
    """Base attendance schema."""
    date: date
    status: AttendanceStatus
    notes: Optional[str] = None


class AttendanceCreate(AttendanceBase):
    """Schema for creating attendance record."""
    student_id: UUID
    class_id: UUID


class AttendanceUpdate(BaseSchema):
    """Schema for updating attendance record."""
    status: Optional[AttendanceStatus] = None
    notes: Optional[str] = None


class AttendanceInDB(AttendanceBase):
    """Schema for attendance in database."""
    id: UUID
    student_id: UUID
    class_id: UUID
    recorded_by: Optional[UUID]
    recorded_at: datetime


class AttendanceResponse(AttendanceInDB):
    """Schema for attendance response."""
    student: UserResponse
    class_: ClassResponse


# Enrollment schemas
class StudentEnrollmentCreate(BaseSchema):
    """Schema for enrolling a student in a class."""
    student_id: UUID
    class_id: UUID


class StudentEnrollmentResponse(BaseSchema):
    """Schema for student enrollment response."""
    id: UUID
    student: UserResponse
    class_: ClassResponse
    enrolled_at: datetime
    is_active: bool


class GuardianStudentCreate(BaseSchema):
    """Schema for creating guardian-student relationship."""
    guardian_id: UUID
    student_id: UUID
    relationship_type: str = Field(..., min_length=1, max_length=50)
    is_primary: bool = False


class GuardianStudentResponse(BaseSchema):
    """Schema for guardian-student relationship response."""
    id: UUID
    guardian: UserResponse
    student: UserResponse
    relationship_type: str
    is_primary: bool
    created_at: datetime


# Pagination schemas
class PaginationParams(BaseSchema):
    """Pagination parameters schema."""
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=1, le=100)

    @property
    def skip(self) -> int:
        """Calculate skip value for database queries."""
        return (self.page - 1) * self.size


class PaginatedResponse(BaseSchema):
    """Paginated response schema."""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
    model_config = ConfigDict(from_attributes=True)


# API Response schemas
class APIResponse(BaseSchema):
    """Standard API response schema."""
    success: bool = True
    message: str = "Success"
    data: Optional[Any] = None


class ErrorResponse(BaseSchema):
    """Error response schema."""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
