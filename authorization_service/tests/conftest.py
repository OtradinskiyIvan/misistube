import pytest
import asyncio
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from authorization_service.src.core.settings import AuthSettings
from authorization_service.src.infrastructure.repositories import UserRepository
from authorization_service.src.services.auth import AuthService
from pydantic import SecretStr


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    return AuthSettings(
        APP_NAME="Test Auth Service",
        JWT_SECRET=SecretStr("x" * 32),
        JWT_ALGORITHM="HS256",
        JWT_ACCESS_EXPIRE_MINUTES=30,
        JWT_REFRESH_EXPIRE_DAYS=7
    )


@pytest.fixture
def mock_session():
    """Mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_user_repo(mock_session):
    """Mock user repository."""
    repo = AsyncMock(spec=UserRepository)
    return repo


@pytest.fixture
def auth_service(mock_user_repo, mock_settings):
    """Auth service with mocked dependencies."""
    return AuthService(mock_user_repo, mock_settings)