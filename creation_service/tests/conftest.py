import pytest
from unittest.mock import AsyncMock
from uuid import UUID, uuid4
from datetime import datetime, timezone
from src.domain.entities.video import Video, VideoStatus


@pytest.fixture
def sample_video():
    return Video(
        id=uuid4(),
        title="Test Video",
        description="Test description",
        storage_key=f"{uuid4()}.mp4",
        status=VideoStatus.UPLOADING,
        duration=120,
        user_id=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_repo():
    repo = AsyncMock()
    repo.add = AsyncMock()
    repo.get = AsyncMock()
    repo.list = AsyncMock(return_value=[])
    repo.count = AsyncMock(return_value=0)
    repo.update = AsyncMock()
    return repo


@pytest.fixture
def mock_storage():
    storage = AsyncMock()
    storage.upload_file = AsyncMock(return_value="test-key.mp4")
    storage.delete_file = AsyncMock()
    storage.get_file_stream = AsyncMock()
    return storage
