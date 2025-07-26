import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
import asyncio
from typing import AsyncGenerator, Generator
import uuid
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="passlib")

from app.main import app
from app.db.models import Base, User, Tenant, Class, StudentClass, GuardianStudent, Quiz, QuizAttempt, AttendanceRecord
from app.core.config import settings
from app.db.database import get_db

# Create test engine
test_engine = create_async_engine(
    "postgresql+asyncpg://sms_user:sms_password@postgres:5432/test_db",
    poolclass=StaticPool,
    echo=True  
)


# Test session maker
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)



@pytest_asyncio.fixture
async def authenticated_org_admin(async_client: AsyncClient, sample_organization_data: dict):
    """Create an organization via the new tenant endpoint and return admin's auth token."""
    # Signup organization (creates admin user)
    response = await async_client.post("/api/tenant/signup/organization", json=sample_organization_data)
    assert response.status_code == 200
    data = response.json()
    admin_email = sample_organization_data["admin_email"]
    admin_password = sample_organization_data["admin_password"]
    # Login admin user
    login_data = {"email": admin_email, "password": admin_password}
    response = await async_client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    token_data = response.json()
    return token_data["access_token"]


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            # Ensure session is closed
            await session.close()
    
    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def async_client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with database dependency override."""
    
    async def get_test_db():
        yield test_db
    
    # Override the database dependency
    app.dependency_overrides[get_db] = get_test_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Clean up dependency overrides
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def sync_client(test_db: AsyncSession) -> Generator[TestClient, None, None]:
    """Create a synchronous test client with database dependency override."""
    
    def get_test_db():
        return test_db
    
    app.dependency_overrides[get_db] = get_test_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def sample_tenant_data():
    """Sample tenant data for testing."""
    return {
        "id": "11111111-1111-1111-1111-111111111111",
        "name": "Test School",
        "is_organization": True,
        "owner_user_id": "22222222-2222-2222-2222-222222222222"
    }

@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": "22222222-2222-2222-2222-222222222222",
        "first_name": "Admin",
        "last_name": "User",
        "email": "admin@testschool.edu",
        "password": "StrongPass123!",
        "role": "admin",
        "tenant_id": "11111111-1111-1111-1111-111111111111",
        "phone_number": "1234567890"
    }

@pytest.fixture
def sample_organization_data():
    """Sample organization signup data for testing."""
    return {
        "organization_name": "Test School",
        "admin_first_name": "Admin",
        "admin_last_name": "User",
        "admin_email": "admin@testschool.edu",
        "admin_password": "StrongPass123!"
    }

@pytest.fixture
def sample_teacher_data():
    """Sample teacher signup data for testing."""
    return {
        "teacher_first_name": "Teacher",
        "teacher_last_name": "User",
        "teacher_email": "teacher@testschool.edu", 
        "teacher_password": "StrongPass123!"
    }

@pytest.fixture
def sample_class_data():
    """Sample class data for testing."""
    return {
        "name": "Test Class",
        "description": "A test class",
        "teacher_id": 1,
        "is_active": True
    }

@pytest.fixture
def sample_quiz_data():
    """Sample quiz data for testing."""
    return {
        "title": "Test Quiz",
        "description": "A test quiz",
        "class_id": 1,
        "max_score": 100,
        "time_limit": 60,
        "is_active": True
    }

@pytest.fixture
async def authenticated_user(async_client: AsyncClient, sample_user_data: dict):
    """Create an authenticated user and return auth token."""
    # Register user
    response = await async_client.post("/api/auth/register", json=sample_user_data)
    assert response.status_code == 201
    
    # Login user
    login_data = {
        "email": sample_user_data["email"],
        "password": sample_user_data["password"]
    }
    response = await async_client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    
    token_data = response.json()
    return token_data["access_token"]

@pytest.fixture
def auth_headers(authenticated_user: str):
    """Create authorization headers with token."""
    return {"Authorization": f"Bearer {authenticated_user}"}

# Test utility functions
def assert_user_response(response_data: dict, expected_data: dict):
    """Assert user response matches expected data."""
    assert response_data["email"] == expected_data["email"]
    assert response_data["first_name"] == expected_data["first_name"]
    assert response_data["last_name"] == expected_data["last_name"]
    assert response_data["role"] == expected_data["role"]
    assert "id" in response_data
    assert "created_at" in response_data
    assert "hashed_password" not in response_data

def assert_class_response(response_data: dict, expected_data: dict):
    """Assert class response matches expected data."""
    assert response_data["name"] == expected_data["name"]
    assert response_data["description"] == expected_data["description"]
    assert response_data["is_active"] == expected_data["is_active"]
    assert "id" in response_data
    assert "created_at" in response_data

def assert_quiz_response(response_data: dict, expected_data: dict):
    """Assert quiz response matches expected data."""
    assert response_data["title"] == expected_data["title"]
    assert response_data["description"] == expected_data["description"]
    assert response_data["max_score"] == expected_data["max_score"]
    assert response_data["time_limit"] == expected_data["time_limit"]
    assert response_data["is_active"] == expected_data["is_active"]
    assert "id" in response_data
    assert "created_at" in response_data