from uuid import UUID, uuid4
from datetime import datetime, timezone
from src.domain.entities.video import Video, VideoStatus
from src.domain.exceptions import VideoNotFoundError, VideoUploadError


class TestVideoStatus:
    def test_values(self):
        assert VideoStatus.UPLOADING.value == "uploading"
        assert VideoStatus.PROCESSING.value == "processing"
        assert VideoStatus.READY.value == "ready"
        assert VideoStatus.FAILED.value == "failed"

    def test_from_string(self):
        assert VideoStatus("uploading") == VideoStatus.UPLOADING
        assert VideoStatus("ready") == VideoStatus.READY

    def test_is_str_enum(self):
        assert isinstance(VideoStatus.UPLOADING, str)


class TestVideo:
    def test_create_minimal(self):
        video = Video.create("Title", "Description", "key.mp4", 0)
        assert isinstance(video.id, UUID)
        assert video.title == "Title"
        assert video.description == "Description"
        assert video.storage_key == "key.mp4"
        assert video.status == VideoStatus.UPLOADING
        assert video.duration == 0
        assert isinstance(video.created_at, datetime)
        assert isinstance(video.updated_at, datetime)

    def test_create_with_duration(self):
        video = Video.create("T", "D", "k.mp4", 300)
        assert video.duration == 300

    def test_dataclass_fields(self, sample_video):
        assert isinstance(sample_video.id, UUID)
        assert sample_video.title == "Test Video"

    def test_dataclass_mutable(self):
        video = Video.create("A", "B", "c.mp4", 10)
        video.title = "Updated"
        assert video.title == "Updated"
        video.status = VideoStatus.READY
        assert video.status == VideoStatus.READY


class TestExceptions:
    def test_video_not_found(self):
        exc = VideoNotFoundError(uuid4())
        assert "not found" in str(exc).lower()

    def test_video_upload_error(self):
        exc = VideoUploadError("S3 upload failed")
        assert "S3 upload failed" in str(exc)
