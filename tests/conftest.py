import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
import asyncio
from typing import AsyncGenerator, Generator

from app.main import app
from app.db.database import get_db
from app.db.models import Base
from app.core.config import settings

# Test database URL - use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)

# Test session maker
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

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
        yield session
    
    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
def client(test_db: AsyncSession) -> Generator[TestClient, None, None]:
    """Create a test client."""
    def get_test_db():
        return test_db
    
    app.dependency_overrides[get_db] = get_test_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "role": "student",
        "phone": "1234567890"
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
async def authenticated_user(client: TestClient, sample_user_data: dict):
    """Create an authenticated user and return auth token."""
    # Register user
    response = client.post("/api/auth/register", json=sample_user_data)
    assert response.status_code == 201
    
    # Login user
    login_data = {
        "email": sample_user_data["email"],
        "password": sample_user_data["password"]
    }
    response = client.post("/api/auth/login", json=login_data)
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
