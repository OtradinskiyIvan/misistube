# src/domain/exceptions.py

class VideoNotFoundError(Exception):
    """Выбрасывается, когда видео не найдено в БД."""
    def __init__(self, video_id=None):
        self.video_id = video_id
        super().__init__(f"Video not found: {video_id}" if video_id else "Video not found")

class VideoUploadError(Exception):
    """Ошибка при загрузке видео в хранилище."""
    pass