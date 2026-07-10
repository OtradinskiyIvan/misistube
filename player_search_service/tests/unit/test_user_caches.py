import time

from src.infrastructure.user_service.avatar_cache import AvatarCacheService
from src.infrastructure.user_service.cache import UserCacheService


class TestUserCacheService:
    def test_set_and_get(self):
        cache = UserCacheService(ttl_seconds=300)
        cache.set("user-1", "alice")
        assert cache.get("user-1") == "alice"

    def test_get_missing(self):
        cache = UserCacheService(ttl_seconds=300)
        assert cache.get("nonexistent") is None

    def test_get_expired(self):
        cache = UserCacheService(ttl_seconds=0)
        cache.set("user-2", "bob")
        time.sleep(0.01)
        assert cache.get("user-2") is None

    def test_set_many(self):
        cache = UserCacheService(ttl_seconds=300)
        cache.set_many({"a": "Alice", "b": "Bob"})
        assert cache.get("a") == "Alice"
        assert cache.get("b") == "Bob"
        assert cache.size() == 2

    def test_clear(self):
        cache = UserCacheService(ttl_seconds=300)
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.clear()
        assert cache.size() == 0

    def test_size(self):
        cache = UserCacheService(ttl_seconds=300)
        assert cache.size() == 0
        cache.set("x", "y")
        assert cache.size() == 1


class TestAvatarCacheService:
    def test_set_and_get(self):
        cache = AvatarCacheService(ttl_seconds=300)
        cache.set("user-1", "https://av.at/1.jpg")
        assert cache.get("user-1") == "https://av.at/1.jpg"

    def test_get_missing(self):
        cache = AvatarCacheService(ttl_seconds=300)
        assert cache.get("nonexistent") is None

    def test_get_expired(self):
        cache = AvatarCacheService(ttl_seconds=0)
        cache.set("user-2", "https://av.at/2.jpg")
        time.sleep(0.01)
        assert cache.get("user-2") is None

    def test_set_none_value(self):
        """Можно закэшировать None — означает, что у пользователя нет аватарки"""
        cache = AvatarCacheService(ttl_seconds=300)
        cache.set("no-avatar", None)
        assert cache.has("no-avatar") is True
        assert cache.get("no-avatar") is None

    def test_has_true(self):
        cache = AvatarCacheService(ttl_seconds=300)
        cache.set("exists", "url")
        assert cache.has("exists") is True

    def test_has_false(self):
        cache = AvatarCacheService(ttl_seconds=300)
        assert cache.has("missing") is False

    def test_has_expired(self):
        cache = AvatarCacheService(ttl_seconds=0)
        cache.set("will-expire", "url")
        time.sleep(0.01)
        assert cache.has("will-expire") is False

    def test_set_many(self):
        cache = AvatarCacheService(ttl_seconds=300)
        cache.set_many({"a": "av-a.jpg", "b": None})
        assert cache.get("a") == "av-a.jpg"
        assert cache.has("b") is True
        assert cache.get("b") is None

    def test_clear_and_size(self):
        cache = AvatarCacheService(ttl_seconds=300)
        cache.set("x", "y")
        cache.set("z", None)
        assert cache.size() == 2
        cache.clear()
        assert cache.size() == 0
