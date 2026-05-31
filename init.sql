-- =============================================
-- Инициализация базы данных для микросервиса Video Studio (MisisTube)
-- =============================================

DO $$ BEGIN
    CREATE TYPE video_status AS ENUM ('uploading', 'processing', 'ready', 'failed');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE OR ALTER videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    storage_key VARCHAR(500) NOT NULL,
    status video_status NOT NULL DEFAULT 'uploading',
    duration_seconds INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_videos_created_at ON videos (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_videos_status ON videos (status);
CREATE INDEX IF NOT EXISTS idx_videos_storage_key ON videos (storage_key);

DROP TRIGGER IF EXISTS trigger_videos_updated_at ON videos;
DROP FUNCTION IF EXISTS update_videos_updated_at();

CREATE OR REPLACE FUNCTION update_videos_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_videos_updated_at
    BEFORE UPDATE ON videos
    FOR EACH ROW
    EXECUTE FUNCTION update_videos_updated_at();

COMMENT ON TABLE videos IS 'Хранит метаданные видео и ссылки на файлы в S3';
COMMENT ON COLUMN videos.id IS 'Уникальный идентификатор видео';
COMMENT ON COLUMN videos.title IS 'Название видео';
COMMENT ON COLUMN videos.description IS 'Описание видео';
COMMENT ON COLUMN videos.storage_key IS 'Ключ объекта в S3 (путь к файлу)';
COMMENT ON COLUMN videos.status IS 'Текущий статус обработки видео';
COMMENT ON COLUMN videos.created_at IS 'Дата и время создания записи';
COMMENT ON COLUMN videos.updated_at IS 'Дата и время последнего обновления записи';