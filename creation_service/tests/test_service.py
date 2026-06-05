import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from src.services.video_service import VideoService
from src.domain.entities.video import Video, VideoStatus
from src.domain.exceptions import VideoNotFoundError, VideoUploadError

pytestmark = pytest.mark.asyncio(loop_scope="function")


class TestVideoService:
    async def test_upload_video(self, mock_repo, mock_storage):
        service = VideoService(mock_repo, mock_storage)
        video = await service.upload_video("Title", "Desc", b"fake_video_data", "test.mp4")
        assert isinstance(video, Video)
        assert video.title == "Title"
        assert video.description == "Desc"
        assert video.status == VideoStatus.READY
        assert video.duration >= 0
        mock_storage.upload_file.assert_awaited_once()
        mock_repo.add.assert_awaited_once()

    async def test_upload_s3_failure_raises(self, mock_repo, mock_storage):
        mock_storage.upload_file.side_effect = Exception("S3 error")
        service = VideoService(mock_repo, mock_storage)
        with pytest.raises(VideoUploadError, match="S3 upload failed"):
            await service.upload_video("T", "D", b"data", "f.mp4")
        mock_repo.add.assert_not_awaited()

    async def test_get_video_metadata_found(self, mock_repo, mock_storage):
        video_id = uuid4()
        expected = Video.create("T", "D", "k.mp4", 10)
        mock_repo.get.return_value = expected
        service = VideoService(mock_repo, mock_storage)
        result = await service.get_video_metadata(video_id)
        assert result == expected

    async def test_get_video_metadata_not_found(self, mock_repo, mock_storage):
        mock_repo.get.return_value = None
        service = VideoService(mock_repo, mock_storage)
        with pytest.raises(VideoNotFoundError):
            await service.get_video_metadata(uuid4())

    async def test_get_video_list(self, mock_repo, mock_storage):
        video = Video.create("T", "D", "k.mp4", 10)
        mock_repo.list.return_value = [video]
        mock_repo.count.return_value = 5
        service = VideoService(mock_repo, mock_storage)
        videos, total = await service.get_video_list(10, 0)
        assert len(videos) == 1
        assert total == 5

    async def test_upload_cleans_up_s3_on_db_failure(self, mock_repo, mock_storage):
        mock_repo.add.side_effect = Exception("DB error")
        service = VideoService(mock_repo, mock_storage)
        with pytest.raises(Exception, match="DB error"):
            await service.upload_video("T", "D", b"data", "f.mp4")
        mock_storage.delete_file.assert_awaited_once()

    async def test_get_presigned_url(self, mock_repo, mock_storage):
        mock_storage.get_presigned_url = AsyncMock(return_value="http://localhost:9000/test.mp4")
        service = VideoService(mock_repo, mock_storage)
        url = await service.get_presigned_url("test.mp4")
        assert "test.mp4" in url
