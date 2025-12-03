"""
Pytest configuration and shared fixtures for backend tests.
Provides test database, client, and authentication utilities.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from unittest.mock import Mock

from app.db.base import Base
from app.main import app
from app.api.v1.endpoints.auth import get_db
from app.services.scheduler import get_scheduler

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Session:
    """Create fresh test database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def mock_scheduler():
    """Mock scheduler to avoid lifecycle issues in tests."""
    mock = Mock()
    mock.add_schedule = Mock(return_value=True)
    mock.remove_schedule = Mock(return_value=True)
    mock.scheduler = Mock()
    mock.scheduler.running = False
    return mock


@pytest.fixture(scope="function")
def client(db: Session, mock_scheduler):
    """Create test client with overridden dependencies."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    def override_get_scheduler():
        return mock_scheduler

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_scheduler] = override_get_scheduler
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(client: TestClient) -> dict:
    """Create admin user and return credentials."""
    credentials = {"username": "admin", "password": "SecurePass123!"}
    response = client.post("/api/v1/auth/setup", json=credentials)
    assert response.status_code == 200, f"Setup failed: {response.json()}"
    return credentials


@pytest.fixture
def admin_token(client: TestClient, admin_user: dict) -> str:
    """Get admin access token."""
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": admin_user["username"],
            "password": admin_user["password"]
        }
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"
    token = response.json()["access_token"]
    return token


@pytest.fixture
def auth_headers(admin_token: str) -> dict:
    """Get authorization headers with token."""
    return {"Authorization": f"Bearer {admin_token}"}
