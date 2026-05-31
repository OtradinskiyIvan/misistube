# src/domain/exceptions.py

class VideoNotFoundError(Exception):
    """Выбрасывается, когда видео не найдено в БД."""
    pass

class VideoUploadError(Exception):
    """Ошибка при загрузке видео в хранилище."""
    pass