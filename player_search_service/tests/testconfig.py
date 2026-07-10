import pytest

from src.core.config import get_settings


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/db")

    config = get_settings()
    assert config.database_url == "postgresql+asyncpg://test:test@localhost/db"


def test_settings_fails_on_missing_env(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(SystemExit):
        get_settings()


# проверочный комментарий для CI 2
