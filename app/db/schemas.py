from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from uuid import UUID
from enum import Enum

from app.db.models import (
    UserStatus, QuizStatus, AttemptStatus, EnrollmentStatus, 
    GuardianStatus, EnrollmentSource, RelationshipType, QuestionType
)


# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True
    )


# ---------- ROLE SCHEMAS ----------
class RoleBase(BaseSchema):
    """Base role schema."""
    role: str = Field(..., description="Role name")


class RoleResponse(RoleBase):
    """Role response schema."""
    pass


# ---------- USER SCHEMAS ----------
class UserBase(BaseSchema):
    """Base user schema."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone_number: Optional[str] = Field(None, max_length=20, description="E.164 format")
    avatar_url: Optional[str] = Field(None, max_length=500)
    locale: str = Field(default='en-GB', max_length=10)


class UserCreate(UserBase):
    """Schema for creating a new user."""
    # Remove password field if using Supabase Auth
    # password: str = Field(..., min_length=8)
    
    # @field_validator('password')
    # def validate_password(cls, v):
    #     if len(v) < 8:
    #         raise ValueError('Password must be at least 8 characters long')
    #     return v


class UserUpdate(BaseSchema):
    """Schema for updating user information."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = Field(None, max_length=500)
    locale: Optional[str] = Field(None, max_length=10)
    is_active: Optional[bool] = None
    status: Optional[UserStatus] = None


class UserInDB(UserBase):
    """Schema for user in database."""
    id: UUID
    status: UserStatus
    is_active: bool
    is_verified: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class UserResponse(UserInDB):
    """Schema for user response (without sensitive data)."""
    user_roles: Optional[List['UserRoleResponse']] = []


# ---------- USER ROLE SCHEMAS ----------
class UserRoleBase(BaseSchema):
    """Base user role schema."""
    role: str
    organization_id: Optional[UUID] = None
    solo_teacher_id: Optional[UUID] = None


class UserRoleCreate(UserRoleBase):
    """Schema for creating user role assignment."""
    user_id: UUID


class UserRoleResponse(UserRoleBase):
    """User role response schema."""
    user_id: UUID
    created_at: datetime
    role_obj: Optional[RoleResponse] = None
    organization: Optional['OrganizationResponse'] = None


# ---------- ORGANIZATION SCHEMAS ----------
class OrganizationBase(BaseSchema):
    """Base organization schema."""
    name: str = Field(..., min_length=1, max_length=200)


class OrganizationCreate(OrganizationBase):
    """Schema for creating organization."""
    owner_user_id: UUID


class OrganizationUpdate(BaseSchema):
    """Schema for updating organization."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    owner_user_id: Optional[UUID] = None


class OrganizationInDB(OrganizationBase):
    """Organization in database schema."""
    id: UUID
    owner_user_id: Optional[UUID]
    created_at: datetime


class OrganizationResponse(OrganizationInDB):
    """Organization response schema."""
    owner: Optional[UserResponse] = None


# ---------- STUDENT PROFILE SCHEMAS ----------
class StudentProfileBase(BaseSchema):
    """Base student profile schema."""
    organization_id: Optional[UUID] = None
    solo_teacher_id: Optional[UUID] = None


class StudentProfileCreate(StudentProfileBase):
    """Schema for creating student profile."""
    student_id: UUID


class StudentProfileResponse(StudentProfileBase):
    """Student profile response schema."""
    student_id: UUID
    created_at: datetime
    organization: Optional[OrganizationResponse] = None
    solo_teacher: Optional[UserResponse] = None


# ---------- COURSE SCHEMAS ----------
class CourseBase(BaseSchema):
    """Base course schema."""
    title: Optional[str] = Field(None, max_length=200)


class CourseCreate(CourseBase):
    """Schema for creating course."""
    organization_id: UUID


class CourseUpdate(BaseSchema):
    """Schema for updating course."""
    title: Optional[str] = Field(None, max_length=200)


class CourseInDB(CourseBase):
    """Course in database schema."""
    id: UUID
    organization_id: UUID
    created_at: datetime


class CourseResponse(CourseInDB):
    """Course response schema."""
    organization: Optional[OrganizationResponse] = None
    teacher_count: Optional[int] = 0
    student_count: Optional[int] = 0


# ---------- QUESTION BANK SCHEMAS ----------
class QuestionBankBase(BaseSchema):
    """Base question bank schema."""
    text: str = Field(..., min_length=1, description="Question prompt/stem")
    qtype: str = Field(..., pattern="^(mcq|essay|true_false|short_answer)$")
    explanation: Optional[str] = None
    difficulty: str = Field(default='dok1', max_length=20)
    points: int = Field(default=1, ge=1)
    time_limit: Optional[int] = Field(None, ge=1, description="Time limit in seconds")
    tags: Optional[List[str]] = []
    media: Optional[Dict[str, Any]] = {}
    meta: Optional[Dict[str, Any]] = {}


class QuestionBankMCQ(QuestionBankBase):
    """MCQ specific question schema."""
    qtype: str = Field(default="mcq", pattern="^mcq$")
    options: List[str] = Field(..., min_items=2)
    correct_answer: int = Field(..., ge=0, description="Index of correct option")


class QuestionBankEssay(QuestionBankBase):
    """Essay specific question schema."""
    qtype: str = Field(default="essay", pattern="^essay$")
    word_limit: Optional[int] = Field(None, ge=1)
    rubric: Optional[Dict[str, Any]] = {}


class QuestionBankTrueFalse(QuestionBankBase):
    """True/False specific question schema."""
    qtype: str = Field(default="true_false", pattern="^true_false$")
    correct_answer: int = Field(..., ge=0, le=1, description="0 for False, 1 for True")


class QuestionBankShortAnswer(QuestionBankBase):
    """Short answer specific question schema."""
    qtype: str = Field(default="short_answer", pattern="^short_answer$")


class QuestionBankCreate(BaseSchema):
    """Schema for creating question bank entry."""
    organization_id: Optional[UUID] = None
    solo_teacher_id: Optional[UUID] = None
    text: str = Field(..., min_length=1)
    qtype: str = Field(..., pattern="^(mcq|essay|true_false|short_answer)$")
    explanation: Optional[str] = None
    options: Optional[List[str]] = None  # For MCQ
    correct_answer: Optional[int] = None  # For MCQ and True/False
    word_limit: Optional[int] = None  # For essay
    rubric: Optional[Dict[str, Any]] = {}  # For essay
    difficulty: str = Field(default='dok1')
    points: int = Field(default=1, ge=1)
    time_limit: Optional[int] = None
    tags: Optional[List[str]] = []
    media: Optional[Dict[str, Any]] = {}
    meta: Optional[Dict[str, Any]] = {}


class QuestionBankUpdate(BaseSchema):
    """Schema for updating question bank entry."""
    text: Optional[str] = Field(None, min_length=1)
    explanation: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[int] = None
    word_limit: Optional[int] = None
    rubric: Optional[Dict[str, Any]] = None
    difficulty: Optional[str] = None
    points: Optional[int] = Field(None, ge=1)
    time_limit: Optional[int] = None
    tags: Optional[List[str]] = None
    media: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None


class QuestionBankInDB(QuestionBankBase):
    """Question bank in database schema."""
    id: UUID
    organization_id: Optional[UUID]
    solo_teacher_id: Optional[UUID]
    options: Optional[List[str]]
    correct_answer: Optional[int]
    word_limit: Optional[int]
    rubric: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class QuestionBankResponse(QuestionBankInDB):
    """Question bank response schema."""
    organization: Optional[OrganizationResponse] = None
    solo_teacher: Optional[UserResponse] = None


# ---------- QUIZ SCHEMAS ----------
class QuizBase(BaseSchema):
    """Base quiz schema."""
    title: Optional[str] = Field(None, max_length=200)


class QuizCreate(QuizBase):
    """Schema for creating quiz."""
    course_id: UUID


class QuizUpdate(BaseSchema):
    """Schema for updating quiz."""
    title: Optional[str] = Field(None, max_length=200)
    published_at: Optional[datetime] = None


class QuizInDB(QuizBase):
    """Quiz in database schema."""
    id: UUID
    course_id: UUID
    published_at: Optional[datetime]
    created_at: datetime


class QuizResponse(QuizInDB):
    """Quiz response schema."""
    course: Optional[CourseResponse] = None
    question_count: Optional[int] = 0


# ---------- QUIZ QUESTION SCHEMAS ----------
class QuizQuestionBase(BaseSchema):
    """Base quiz question schema."""
    position: Optional[int] = None
    points: int = Field(default=1, ge=1)
    randomize: bool = Field(default=False)
    show_explanation: bool = Field(default=True)


class QuizQuestionCreate(QuizQuestionBase):
    """Schema for creating quiz question link."""
    quiz_id: UUID
    question_id: UUID


class QuizQuestionUpdate(BaseSchema):
    """Schema for updating quiz question link."""
    position: Optional[int] = None
    points: Optional[int] = Field(None, ge=1)
    randomize: Optional[bool] = None
    show_explanation: Optional[bool] = None


class QuizQuestionResponse(QuizQuestionBase):
    """Quiz question response schema."""
    quiz_id: UUID
    question_id: UUID
    created_at: datetime
    question: Optional[QuestionBankResponse] = None


# ---------- QUIZ ATTEMPT SCHEMAS ----------
class QuizAttemptBase(BaseSchema):
    """Base quiz attempt schema."""
    answers: List[Dict[str, Any]] = Field(default_factory=list)


class QuizAttemptCreate(QuizAttemptBase):
    """Schema for creating quiz attempt."""
    quiz_id: UUID


class QuizAttemptUpdate(BaseSchema):
    """Schema for updating quiz attempt."""
    answers: Optional[List[Dict[str, Any]]] = None
    status: Optional[AttemptStatus] = None
    finished_at: Optional[datetime] = None
    time_spent: Optional[int] = None
    score: Optional[float] = None
    percentage: Optional[float] = None
    security_violations: Optional[List[Dict[str, Any]]] = None
    flagged_for_review: Optional[bool] = None


class QuizAttemptInDB(QuizAttemptBase):
    """Quiz attempt in database schema."""
    id: UUID
    quiz_id: Optional[UUID]
    student_id: Optional[UUID]
    started_at: datetime
    finished_at: Optional[datetime]
    time_spent: Optional[int]
    status: AttemptStatus
    score: Optional[float]
    percentage: Optional[float]
    questions_seen: Optional[List[str]]
    security_violations: List[Dict[str, Any]]
    device_info: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    flagged_for_review: bool
    created_at: datetime


class QuizAttemptResponse(QuizAttemptInDB):
    """Quiz attempt response schema."""
    quiz: Optional[QuizResponse] = None
    student: Optional[UserResponse] = None


# ---------- GUARDIAN-CHILD SCHEMAS ----------
class GuardianChildBase(BaseSchema):
    """Base guardian-child schema."""
    relationship: str = Field(default='parent', max_length=50)
    nickname: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    communication_prefs: Dict[str, Any] = Field(default_factory=dict)
    preferences: Dict[str, Any] = Field(default_factory=dict)


class GuardianChildCreate(GuardianChildBase):
    """Schema for creating guardian-child relationship."""
    guardian_id: UUID
    student_id: UUID


class GuardianChildUpdate(BaseSchema):
    """Schema for updating guardian-child relationship."""
    relationship: Optional[str] = Field(None, max_length=50)
    nickname: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    status: Optional[GuardianStatus] = None
    communication_prefs: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None


class GuardianChildInDB(GuardianChildBase):
    """Guardian-child in database schema."""
    guardian_id: UUID
    student_id: UUID
    status: GuardianStatus
    verified_at: Optional[datetime]
    last_sync_at: Optional[datetime]
    created_at: datetime


class GuardianChildResponse(GuardianChildInDB):
    """Guardian-child response schema."""
    guardian: Optional[UserResponse] = None
    child: Optional[UserResponse] = None


# ---------- STUDENT ENROLLMENT SCHEMAS ----------
class StudentEnrollmentBase(BaseSchema):
    """Base student enrollment schema."""
    status: EnrollmentStatus = Field(default=EnrollmentStatus.ACTIVE)
    role: str = Field(default='student', max_length=20)
    source: str = Field(default='admin_add', max_length=20)


class StudentEnrollmentCreate(StudentEnrollmentBase):
    """Schema for creating student enrollment."""
    student_id: UUID
    course_id: UUID


class StudentEnrollmentUpdate(BaseSchema):
    """Schema for updating student enrollment."""
    status: Optional[EnrollmentStatus] = None
    role: Optional[str] = Field(None, max_length=20)
    completed_at: Optional[datetime] = None
    grade: Optional[float] = Field(None, ge=0, le=100)
    progress: Optional[Dict[str, Any]] = None


class StudentEnrollmentInDB(StudentEnrollmentBase):
    """Student enrollment in database schema."""
    student_id: UUID
    course_id: UUID
    enrolled_at: datetime
    completed_at: Optional[datetime]
    grade: Optional[float]
    progress: Dict[str, Any]
    updated_at: datetime


class StudentEnrollmentResponse(StudentEnrollmentInDB):
    """Student enrollment response schema."""
    student: Optional[UserResponse] = None
    course: Optional[CourseResponse] = None


# ---------- AUTHENTICATION SCHEMAS ----------
class Token(BaseSchema):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseSchema):
    """Token data schema."""
    user_id: Optional[UUID] = None
    email: Optional[str] = None
    roles: Optional[List[str]] = []


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


# ---------- REGISTRATION SCHEMAS ----------
class OrganizationSignUp(BaseSchema):
    """Schema for organization registration."""
    organization_name: str = Field(..., min_length=2, max_length=200)
    admin_first_name: str = Field(..., min_length=1, max_length=100)
    admin_last_name: str = Field(..., min_length=1, max_length=100)
    admin_email: EmailStr
    admin_password: str = Field(..., min_length=8)


class TeacherSignUp(BaseSchema):
    """Schema for solo teacher registration."""
    teacher_first_name: str = Field(..., min_length=1, max_length=100)
    teacher_last_name: str = Field(..., min_length=1, max_length=100)
    teacher_email: EmailStr
    teacher_password: str = Field(..., min_length=8)


class SignUpResponse(BaseSchema):
    """Standard response for sign-up endpoints."""
    success: bool = True
    message: str = "Registration successful"
    user_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None


# ---------- PAGINATION SCHEMAS ----------
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


# ---------- API RESPONSE SCHEMAS ----------
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


# ---------- TEACHER COURSE SCHEMAS ----------
class TeacherCourseCreate(BaseSchema):
    """Schema for assigning teacher to course."""
    teacher_id: UUID
    course_id: UUID


class TeacherCourseResponse(BaseSchema):
    """Teacher course response schema."""
    teacher_id: UUID
    course_id: UUID
    created_at: datetime
    teacher: Optional[UserResponse] = None
    course: Optional[CourseResponse] = None


# ---------- ADMIN COURSE RIGHTS SCHEMAS ----------
class OrgAdminCourseRightCreate(BaseSchema):
    """Schema for granting admin course rights."""
    admin_id: UUID
    course_id: UUID


class OrgAdminCourseRightResponse(BaseSchema):
    """Admin course rights response schema."""
    admin_id: UUID
    course_id: UUID
    created_at: datetime
    admin: Optional[UserResponse] = None
    course: Optional[CourseResponse] = None


# ---------- STUDENT ENROLLMENT SCHEMAS ----------
class StudentEnrollmentBase(BaseSchema):
    """Base student enrollment schema."""
    status: EnrollmentStatus = EnrollmentStatus.ACTIVE
    role: str = "student"
    source: EnrollmentSource = EnrollmentSource.ADMIN_ADD


class StudentEnrollmentCreate(StudentEnrollmentBase):
    """Schema for creating student enrollment."""
    student_id: UUID
    course_id: UUID


class StudentEnrollmentUpdate(BaseSchema):
    """Schema for updating student enrollment."""
    status: Optional[EnrollmentStatus] = None
    grade: Optional[float] = None
    progress: Optional[Dict[str, Any]] = None


class StudentEnrollmentResponse(StudentEnrollmentBase):
    """Student enrollment response schema."""
    student_id: UUID
    course_id: UUID
    enrolled_at: datetime
    completed_at: Optional[datetime] = None
    grade: Optional[float] = None
    progress: Optional[Dict[str, Any]] = None
    updated_at: datetime
    student: Optional[UserResponse] = None
    course: Optional[CourseResponse] = None


# ---------- GUARDIAN CHILD SCHEMAS ----------
class GuardianChildBase(BaseSchema):
    """Base guardian child schema."""
    relationship: RelationshipType = RelationshipType.PARENT
    nickname: Optional[str] = None
    status: GuardianStatus = GuardianStatus.PENDING


class GuardianChildCreate(GuardianChildBase):
    """Schema for creating guardian-child relationship."""
    guardian_id: UUID
    student_id: UUID


class GuardianChildUpdate(BaseSchema):
    """Schema for updating guardian-child relationship."""
    nickname: Optional[str] = None
    status: Optional[GuardianStatus] = None
    communication_prefs: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None


class GuardianChildResponse(GuardianChildBase):
    """Guardian child response schema."""
    guardian_id: UUID
    student_id: UUID
    avatar_url: Optional[str] = None
    verified_at: Optional[datetime] = None
    last_sync_at: Optional[datetime] = None
    communication_prefs: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    created_at: datetime
    guardian: Optional[UserResponse] = None
    child: Optional[UserResponse] = None


# Forward reference updates for nested relationships
UserResponse.model_rebuild()
UserRoleResponse.model_rebuild()
OrganizationResponse.model_rebuild()
CourseResponse.model_rebuild()
QuestionBankResponse.model_rebuild()
QuizResponse.model_rebuild()
QuizQuestionResponse.model_rebuild()
QuizAttemptResponse.model_rebuild()
StudentEnrollmentResponse.model_rebuild()
GuardianChildResponse.model_rebuild()
GuardianChildResponse.model_rebuild()
StudentEnrollmentResponse.model_rebuild()
TeacherCourseResponse.model_rebuild()
OrgAdminCourseRightResponse.model_rebuild()