import sys
from pathlib import Path
from typing import AsyncGenerator
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from pytest import FixtureRequest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

SHARED = ROOT.parent
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))

from datetime import datetime

from src.domain.entities import User
from src.domain.interfaces import UnitOfWork, UserRepository


@pytest.fixture
def mock_repository(request: FixtureRequest) -> AsyncMock:
    mock = AsyncMock(spec=UserRepository)
    return mock


@pytest.fixture
def mock_uow(request: FixtureRequest) -> AsyncMock:
    mock = AsyncMock(spec=UnitOfWork)
    return mock


@pytest.fixture
def sample_user_id() -> UUID:
    return uuid4()


@pytest.fixture
def sample_user(sample_user_id: UUID) -> User:
    return User(
        id=sample_user_id,
        username="testuser",
        email="test@example.com",
        status="active",
        created_at=datetime(2026, 1, 1, 12, 0, 0),
        updated_at=datetime(2026, 1, 1, 12, 0, 0),
    )
