from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, delete
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date

from app.db.models import (
    User, UserRole, Role, Organization, StudentProfile,
    Course, TeacherCourse, OrgAdminCourseRight,
    Quiz, QuizQuestion, QuizAttempt, QuestionBank,
    GuardianChild, StudentEnrollment,
    UserStatus, QuizStatus, AttemptStatus, EnrollmentStatus, GuardianStatus
)
from app.db.schemas import (
    UserCreate, UserUpdate, UserRoleCreate, 
    OrganizationCreate, OrganizationUpdate,
    CourseCreate, CourseUpdate,
    QuizCreate, QuizUpdate, QuizQuestionCreate, QuizQuestionUpdate,
    QuizAttemptCreate, QuizAttemptUpdate,
    StudentEnrollmentCreate, StudentEnrollmentUpdate,
    QuestionBankCreate, QuestionBankUpdate,
    OrganizationSignUp, TeacherSignUp
)
from app.core.security import security
from app.exceptions.custom_exceptions import (
    UserNotFoundException, UserAlreadyExistsException,
    ClassNotFoundException, QuizNotFoundException,
    StudentNotEnrolledException, ConflictException
)


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


class CRUDCourse(CRUDBase):
    """CRUD operations for Course model."""
    
    async def get_with_teachers(self, db: AsyncSession, id: UUID) -> Optional[Course]:
        """Get course with teacher information."""
        result = await db.execute(
            select(Course)
            .options(selectinload(Course.teacher_courses))
            .where(Course.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_organization(self, db: AsyncSession, *, organization_id: UUID, skip: int = 0, limit: int = 100) -> List[Course]:
        """Get courses by organization."""
        return await self.get_multi(db, skip=skip, limit=limit, organization_id=organization_id)
    
    async def create(self, db: AsyncSession, *, obj_in: CourseCreate) -> Course:
        """Create a new course."""
        course_data = obj_in.model_dump()
        return await super().create(db, obj_in=course_data)
    
    async def enroll_student(self, db: AsyncSession, *, course_id: UUID, student_id: UUID) -> StudentEnrollment:
        """Enroll a student in a course."""
        # Check if already enrolled
        existing = await db.execute(
            select(StudentEnrollment).where(
                and_(
                    StudentEnrollment.course_id == course_id,
                    StudentEnrollment.student_id == student_id,
                    StudentEnrollment.status == EnrollmentStatus.ACTIVE
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictException("Student is already enrolled in this course")
        
        enrollment = StudentEnrollment(course_id=course_id, student_id=student_id)
        db.add(enrollment)
        await db.commit()
        await db.refresh(enrollment)
        return enrollment
    
    async def get_enrolled_students(self, db: AsyncSession, *, course_id: UUID) -> List[User]:
        """Get students enrolled in a course."""
        result = await db.execute(
            select(User)
            .join(StudentEnrollment, User.id == StudentEnrollment.student_id)
            .where(
                and_(
                    StudentEnrollment.course_id == course_id,
                    StudentEnrollment.status == EnrollmentStatus.ACTIVE
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


class CRUDOrganization(CRUDBase):
    """CRUD operations for Organization model."""
    
    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Organization]:
        """Get organization by name."""
        result = await db.execute(select(Organization).where(Organization.name == name))
        return result.scalar_one_or_none()


class CRUDUserRole(CRUDBase):
    """CRUD operations for UserRole model."""
    
    async def get_user_roles(self, db: AsyncSession, user_id: UUID) -> List[UserRole]:
        """Get all roles for a user."""
        result = await db.execute(
            select(UserRole).where(UserRole.user_id == user_id)
        )
        return result.scalars().all()
    
    async def user_has_role(self, db: AsyncSession, user_id: UUID, role: str, organization_id: Optional[UUID] = None) -> bool:
        """Check if user has specific role."""
        query = select(UserRole).where(
            and_(UserRole.user_id == user_id, UserRole.role == role)
        )
        if organization_id:
            query = query.where(UserRole.organization_id == organization_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None


class CRUDStudentEnrollment(CRUDBase):
    """CRUD operations for StudentEnrollment model."""
    
    async def get_student_courses(self, db: AsyncSession, student_id: UUID) -> List[StudentEnrollment]:
        """Get all active enrollments for a student."""
        result = await db.execute(
            select(StudentEnrollment)
            .where(
                and_(
                    StudentEnrollment.student_id == student_id,
                    StudentEnrollment.status == EnrollmentStatus.ACTIVE
                )
            )
        )
        return result.scalars().all()


class CRUDQuestionBank(CRUDBase):
    """CRUD operations for QuestionBank model."""
    
    async def get_by_provider(self, db: AsyncSession, organization_id: Optional[UUID] = None, solo_teacher_id: Optional[UUID] = None) -> List[QuestionBank]:
        """Get questions by provider."""
        if organization_id:
            query = select(QuestionBank).where(QuestionBank.organization_id == organization_id)
        elif solo_teacher_id:
            query = select(QuestionBank).where(QuestionBank.solo_teacher_id == solo_teacher_id)
        else:
            return []
        
        result = await db.execute(query)
        return result.scalars().all()


class CRUDGuardianChild(CRUDBase):
    """CRUD operations for GuardianChild model."""
    
    async def get_guardian_children(self, db: AsyncSession, guardian_id: UUID) -> List[GuardianChild]:
        """Get all children for a guardian."""
        result = await db.execute(
            select(GuardianChild)
            .where(
                and_(
                    GuardianChild.guardian_id == guardian_id,
                    GuardianChild.status == GuardianStatus.ACCEPTED
                )
            )
        )
        return result.scalars().all()


# Create CRUD instances
user = CRUDUser(User)
organization = CRUDOrganization(Organization)
user_role = CRUDUserRole(UserRole)
course = CRUDCourse(Course) 
student_enrollment = CRUDStudentEnrollment(StudentEnrollment)
question_bank = CRUDQuestionBank(QuestionBank)
guardian_child = CRUDGuardianChild(GuardianChild)
quiz = CRUDQuiz(Quiz)
quiz_question = CRUDQuizQuestion(QuizQuestion)
quiz_attempt = CRUDQuizAttempt(QuizAttempt)

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

# Course-related convenience functions
async def get_course_by_id(db: AsyncSession, course_id: UUID) -> Optional[Course]:
    """Get course by ID"""
    return await course.get(db, id=course_id)

async def get_course_by_title(db: AsyncSession, title: str, organization_id: UUID) -> Optional[Course]:
    """Get course by title within organization"""
    result = await db.execute(
        select(Course).where(
            and_(Course.title == title, Course.organization_id == organization_id)
        )
    )
    return result.scalar_one_or_none()

async def create_course(db: AsyncSession, course_create: CourseCreate) -> Course:
    """Create course"""
    return await course.create(db, obj_in=course_create)

async def get_student_courses(db: AsyncSession, student_id: UUID) -> List[Course]:
    """Get all courses for a student"""
    result = await db.execute(
        select(Course)
        .join(StudentEnrollment)
        .where(
            and_(
                StudentEnrollment.student_id == student_id,
                StudentEnrollment.status == EnrollmentStatus.ACTIVE
            )
        )
    )
    return result.scalars().all()

async def get_student_enrollment(db: AsyncSession, student_id: UUID, course_id: UUID) -> Optional[StudentEnrollment]:
    """Get student course enrollment"""
    result = await db.execute(
        select(StudentEnrollment)
        .where(
            and_(
                StudentEnrollment.student_id == student_id, 
                StudentEnrollment.course_id == course_id
            )
        )
    )
    return result.scalar_one_or_none()

async def create_student_enrollment(db: AsyncSession, student_id: UUID, course_id: UUID, source: str = "admin_add") -> StudentEnrollment:
    """Create student course enrollment"""
    enrollment = StudentEnrollment(
        student_id=student_id, 
        course_id=course_id,
        source=source
    )
    db.add(enrollment)
    await db.commit()
    await db.refresh(enrollment)
    return enrollment

async def update_enrollment_status(db: AsyncSession, student_id: UUID, course_id: UUID, status: EnrollmentStatus) -> bool:
    """Update student enrollment status"""
    result = await db.execute(
        select(StudentEnrollment)
        .where(
            and_(
                StudentEnrollment.student_id == student_id,
                StudentEnrollment.course_id == course_id
            )
        )
    )
    enrollment = result.scalar_one_or_none()
    if enrollment:
        enrollment.status = status
        await db.commit()
        return True
    return False

async def get_course_students(db: AsyncSession, course_id: UUID) -> List[User]:
    """Get all students in a course"""
    result = await db.execute(
        select(User)
        .join(StudentEnrollment)
        .where(
            and_(
                StudentEnrollment.course_id == course_id,
                StudentEnrollment.status == EnrollmentStatus.ACTIVE
            )
        )
    )
    return result.scalars().all()

async def get_course_statistics(db: AsyncSession, course_id: UUID) -> dict:
    """Get course statistics"""
    try:
        student_count = await db.scalar(
            select(func.count(StudentEnrollment.student_id))
            .where(
                and_(
                    StudentEnrollment.course_id == course_id,
                    StudentEnrollment.status == EnrollmentStatus.ACTIVE
                )
            )
        )
        
        quiz_count = await db.scalar(
            select(func.count(Quiz.id))
            .where(Quiz.course_id == course_id)
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

async def get_student_quizzes(db: AsyncSession, student_id: UUID, course_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[Quiz]:
    """Get quizzes available to a student"""
    query = (
        select(Quiz)
        .join(Course)
        .join(StudentEnrollment)
        .where(
            and_(
                StudentEnrollment.student_id == student_id,
                StudentEnrollment.status == EnrollmentStatus.ACTIVE
            )
        )
    )
    
    if course_id:
        query = query.where(Quiz.course_id == course_id)
    
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
async def get_guardian_children(db: AsyncSession, guardian_id: UUID) -> List[User]:
    """Get all children under a guardian"""
    result = await db.execute(
        select(User)
        .join(GuardianChild)
        .where(
            and_(
                GuardianChild.guardian_id == guardian_id,
                GuardianChild.status == GuardianStatus.ACCEPTED
            )
        )
    )
    return result.scalars().all()

async def get_guardian_child_relationship(db: AsyncSession, guardian_id: UUID, student_id: UUID) -> Optional[GuardianChild]:
    """Get guardian-child relationship"""
    result = await db.execute(
        select(GuardianChild)
        .where(
            and_(
                GuardianChild.guardian_id == guardian_id, 
                GuardianChild.student_id == student_id
            )
        )
    )
    return result.scalar_one_or_none()

async def create_guardian_child_relationship(db: AsyncSession, guardian_id: UUID, student_id: UUID, relationship: str = "parent") -> GuardianChild:
    """Create guardian-child relationship"""
    guardian_child = GuardianChild(
        guardian_id=guardian_id,
        student_id=student_id,
        relationship=relationship
    )
    db.add(guardian_child)
    await db.commit()
    await db.refresh(guardian_child)
    return guardian_child

async def get_guardian_overview(db: AsyncSession, guardian_id: UUID) -> dict:
    """Get overview for guardian"""
    try:
        children = await get_guardian_children(db, guardian_id)
        
        overview = {
            "total_children": len(children),
            "children": [
                {
                    "id": child.id,
                    "name": f"{child.first_name} {child.last_name}",
                    "email": child.email
                }
                for child in children
            ]
        }
        
        return overview
    except Exception:
        return {}


# Organization and Solo Teacher signup functions

async def create_organization_signup(db: AsyncSession, signup: OrganizationSignUp):
    """Create organization with admin user"""
    existing_user = await user.get_by_email(db, email=signup.admin_email)
    if existing_user:
        raise UserAlreadyExistsException(signup.admin_email)

    try:
        # Step 1: Create organization first
        organization_obj = Organization(
            name=signup.organization_name,
        )
        db.add(organization_obj)
        await db.flush()

        # Step 2: Create admin user
        admin_user = User(
            first_name=signup.admin_first_name,
            last_name=signup.admin_last_name,
            email=signup.admin_email,
            is_active=True
        )
        db.add(admin_user)
        await db.flush()

        # Step 3: Assign the admin as the organization owner
        organization_obj.owner_user_id = admin_user.id
        
        # Step 4: Create user role
        admin_role = UserRole(
            user_id=admin_user.id,
            role="org_owner",
            organization_id=organization_obj.id
        )
        db.add(admin_role)
        
        await db.commit()
        await db.refresh(admin_user)
        await db.refresh(organization_obj)

        return admin_user, organization_obj

    except Exception as e:
        await db.rollback()
        raise e
        await db.rollback()
        raise e

async def create_teacher_signup(db: AsyncSession, signup: TeacherSignUp):
    """Create a new solo teacher user with self-managed profile."""

    # Check if teacher email already exists
    existing_user = await user.get_by_email(db, email=signup.teacher_email)
    if existing_user:
        raise UserAlreadyExistsException(signup.teacher_email)

    try:
        # Step 1: Create teacher user
        teacher_user = User(
            first_name=signup.teacher_first_name,
            last_name=signup.teacher_last_name,
            email=signup.teacher_email,
            is_active=True
        )
        db.add(teacher_user)
        await db.flush()

        # Step 2: Create user role as solo teacher
        teacher_role = UserRole(
            user_id=teacher_user.id,
            role="solo_teacher",
            solo_teacher_id=teacher_user.id  # self-reference
        )
        db.add(teacher_role)
        
        await db.commit()
        await db.refresh(teacher_user)

        return teacher_user

    except Exception as e:
        await db.rollback()
        raise e
