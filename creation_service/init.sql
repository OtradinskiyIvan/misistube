-- =============================================
-- Только то, что не умеет SQLAlchemy:
-- пользователи, расширения и т.п.
-- =============================================

-- Пользователь для микросервиса поиска/плеера (player_and_search)
DO $$ BEGIN
    CREATE USER player_search_reader WITH PASSWORD 'player_search_password';
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- Права (игнорируем ошибки, если уже выданы)
GRANT CONNECT ON DATABASE video_db TO player_search_reader;
GRANT USAGE ON SCHEMA public TO player_search_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO player_search_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO player_search_reader;
