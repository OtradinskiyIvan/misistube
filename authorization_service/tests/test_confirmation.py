from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from pydantic import SecretStr

from ..src.core.settings import AuthSettings
from ..src.services.confirmation import (
    _CODES,
    _PENDING,
    CODE_TTL_MINUTES,
    _store_code,
    _store_pending,
    create_pending_registration,
    generate_code,
    pop_pending,
    send_email_sync,
    verify_code,
)


@pytest.fixture
def mock_settings():
    """Mock settings for SMTP testing."""
    return AuthSettings(
        APP_NAME="Test Auth Service",
        JWT_SECRET=SecretStr("x" * 32),
        JWT_ALGORITHM="HS256",
        JWT_ACCESS_EXPIRE_MINUTES=30,
        JWT_REFRESH_EXPIRE_DAYS=7,
        DATABASE_URL="postgresql://test:test@localhost:5432/testdb",
        S3_ENDPOINT="http://localhost:9000",
        S3_ACCESS_KEY=SecretStr("test-access-key"),
        S3_SECRET_KEY=SecretStr("test-secret-key"),
        S3_BUCKET_NAME="test-bucket",
        SMTP_HOST="smtp.example.com",
        SMTP_PORT=587,
        SMTP_USER="test@example.com",
        SMTP_PASSWORD="password",
        SMTP_USE_TLS=True,
        SMTP_FROM="noreply@example.com",
    )


@pytest.fixture(autouse=True)
def clear_stores():
    """Clear in-memory stores before each test."""
    _CODES.clear()
    _PENDING.clear()
    yield
    _CODES.clear()
    _PENDING.clear()


class TestGenerateCode:
    def test_generate_code_returns_string(self):
        """Test that generate_code returns a string."""
        code = generate_code()
        assert isinstance(code, str)

    def test_generate_code_is_6_digits(self):
        """Test that generated code is 6 digits."""
        code = generate_code()
        assert len(code) == 6
        assert code.isdigit()

    def test_generate_code_is_between_0_and_999999(self):
        """Test that generated code is in valid range."""
        code = generate_code()
        assert 0 <= int(code) <= 999999

    def test_generate_code_randomness(self):
        """Test that codes are not always the same."""
        codes = {generate_code() for _ in range(100)}
        assert len(codes) > 1  # At least some variation


class TestStoreCode:
    def test_store_code_stores_code_and_expiry(self):
        """Test that _store_code stores code with expiry."""
        email = "test@example.com"
        code = "123456"

        _store_code(email, code)

        assert email.lower() in _CODES
        stored_code, expires = _CODES[email.lower()]
        assert stored_code == code
        assert isinstance(expires, datetime)

    def test_store_code_expiry_is_correct(self):
        """Test that expiry time is set correctly."""
        email = "test@example.com"
        code = "123456"
        before = datetime.utcnow()

        _store_code(email, code)

        _, expires = _CODES[email.lower()]
        after = datetime.utcnow()

        expected_expires_min = before + timedelta(minutes=CODE_TTL_MINUTES)
        expected_expires_max = after + timedelta(minutes=CODE_TTL_MINUTES)

        assert expected_expires_min <= expires <= expected_expires_max

    def test_store_code_email_case_insensitive(self):
        """Test that email storage is case-insensitive."""
        email1 = "Test@Example.com"
        email2 = "test@example.com"
        code = "123456"

        _store_code(email1, code)

        assert email2.lower() in _CODES


class TestStorePending:
    def test_store_pending_stores_data(self):
        """Test that _store_pending stores username and password."""
        email = "test@example.com"
        username = "testuser"
        hashed_password = "hashed_pwd_123"

        _store_pending(email, username, hashed_password)

        assert email.lower() in _PENDING
        stored_username, stored_password, expires = _PENDING[email.lower()]
        assert stored_username == username
        assert stored_password == hashed_password

    def test_store_pending_expiry_is_correct(self):
        """Test that expiry time is set correctly."""
        email = "test@example.com"
        before = datetime.utcnow()

        _store_pending(email, "user", "pwd")

        _, _, expires = _PENDING[email.lower()]
        after = datetime.utcnow()

        expected_expires_min = before + timedelta(minutes=CODE_TTL_MINUTES)
        expected_expires_max = after + timedelta(minutes=CODE_TTL_MINUTES)

        assert expected_expires_min <= expires <= expected_expires_max


class TestVerifyCode:
    def test_verify_code_valid_code(self):
        """Test verifying a valid code."""
        email = "test@example.com"
        code = "123456"
        _store_code(email, code)

        result = verify_code(email, code)

        assert result is True
        assert email.lower() not in _CODES  # Code should be removed after verification

    def test_verify_code_invalid_code(self):
        """Test verifying with wrong code."""
        email = "test@example.com"
        code = "123456"
        _store_code(email, code)

        result = verify_code(email, "999999")

        assert result is False
        assert email.lower() in _CODES  # Code should still exist

    def test_verify_code_nonexistent_email(self):
        """Test verifying code for email with no code."""
        result = verify_code("nonexistent@example.com", "123456")

        assert result is False

    def test_verify_code_expired_code(self):
        """Test verifying an expired code."""
        email = "test@example.com"
        code = "123456"
        # Manually store with already expired time
        _CODES[email.lower()] = (code, datetime.utcnow() - timedelta(seconds=1))

        result = verify_code(email, code)

        assert result is False
        assert email.lower() not in _CODES  # Expired code should be removed

    def test_verify_code_case_insensitive_email(self):
        """Test that email verification is case-insensitive."""
        email1 = "Test@Example.com"
        email2 = "test@example.com"
        code = "123456"
        _store_code(email1, code)

        result = verify_code(email2, code)

        assert result is True

    def test_verify_code_removes_expired_pending(self):
        """Test that expired pending is removed when code expires."""
        email = "test@example.com"
        code = "123456"
        _CODES[email.lower()] = (code, datetime.utcnow() - timedelta(seconds=1))
        _PENDING[email.lower()] = ("user", "pwd", datetime.utcnow() - timedelta(seconds=1))

        verify_code(email, code)

        assert email.lower() not in _PENDING


class TestPopPending:
    def test_pop_pending_returns_data(self):
        """Test that pop_pending returns stored data."""
        email = "test@example.com"
        username = "testuser"
        hashed_password = "hashed_pwd_123"
        _store_pending(email, username, hashed_password)

        result = pop_pending(email)

        assert result == (username, hashed_password)
        assert email.lower() not in _PENDING  # Should be removed

    def test_pop_pending_nonexistent_email(self):
        """Test pop_pending with nonexistent email."""
        result = pop_pending("nonexistent@example.com")

        assert result is None

    def test_pop_pending_expired_data(self):
        """Test that expired pending data is not returned."""
        email = "test@example.com"
        _PENDING[email.lower()] = ("user", "pwd", datetime.utcnow() - timedelta(seconds=1))

        result = pop_pending(email)

        assert result is None

    def test_pop_pending_case_insensitive_email(self):
        """Test that email lookup is case-insensitive."""
        email1 = "Test@Example.com"
        email2 = "test@example.com"
        username = "testuser"
        hashed_password = "hashed_pwd_123"
        _store_pending(email1, username, hashed_password)

        result = pop_pending(email2)

        assert result == (username, hashed_password)


class TestSendEmailSync:
    def test_send_email_sync_with_tls(self, mock_settings):
        """Test sending email with TLS enabled."""
        mock_settings.SMTP_USE_TLS = True

        with patch("smtplib.SMTP") as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            send_email_sync(
                "recipient@example.com",
                "Test Subject",
                "Test Body",
                mock_settings
            )

            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with(
                mock_settings.SMTP_USER,
                mock_settings.SMTP_PASSWORD
            )
            mock_server.sendmail.assert_called_once()

    def test_send_email_sync_without_tls(self, mock_settings):
        """Test sending email without TLS."""
        mock_settings.SMTP_USE_TLS = False

        with patch("smtplib.SMTP") as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            send_email_sync(
                "recipient@example.com",
                "Test Subject",
                "Test Body",
                mock_settings
            )

            mock_server.starttls.assert_not_called()
            mock_server.login.assert_called_once()
            mock_server.sendmail.assert_called_once()

    def test_send_email_sync_without_credentials(self, mock_settings):
        """Test sending email without username and password."""
        mock_settings.SMTP_USER = None
        mock_settings.SMTP_PASSWORD = None
        mock_settings.SMTP_USE_TLS = False

        with patch("smtplib.SMTP") as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            send_email_sync(
                "recipient@example.com",
                "Test Subject",
                "Test Body",
                mock_settings
            )

            mock_server.login.assert_not_called()
            mock_server.sendmail.assert_called_once()

    def test_send_email_sync_uses_custom_from_address(self, mock_settings):
        """Test that custom SMTP_FROM is used."""
        mock_settings.SMTP_FROM = "custom@example.com"

        with patch("smtplib.SMTP") as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            send_email_sync(
                "recipient@example.com",
                "Test Subject",
                "Test Body",
                mock_settings
            )

            call_args = mock_server.sendmail.call_args
            assert call_args[0][0] == "custom@example.com"

    def test_send_email_sync_default_from_address(self, mock_settings):
        """Test default SMTP_FROM when not set."""
        mock_settings.SMTP_FROM = None

        with patch("smtplib.SMTP") as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            send_email_sync(
                "recipient@example.com",
                "Test Subject",
                "Test Body",
                mock_settings
            )

            call_args = mock_server.sendmail.call_args
            assert f"no-reply@{mock_settings.SMTP_HOST}" in call_args[0][0]


class TestCreatePendingRegistration:
    def test_create_pending_registration_success(self, mock_settings, event_loop):
        """Test successful pending registration creation."""
        async def test():
            with patch("asyncio.to_thread") as mock_thread:
                mock_thread.return_value = None

                code = await create_pending_registration(
                    "testuser",
                    "test@example.com",
                    "password123",
                    mock_settings
                )

                assert isinstance(code, str)
                assert len(code) == 6
                assert code.isdigit()
                assert "test@example.com" in _CODES
                assert "test@example.com" in _PENDING

        event_loop.run_until_complete(test())

    def test_create_pending_registration_stores_hashed_password(self, mock_settings, event_loop):
        """Test that password is hashed in pending."""
        async def test():
            with patch("asyncio.to_thread") as mock_thread:
                mock_thread.return_value = None

                code = await create_pending_registration(
                    "testuser",
                    "test@example.com",
                    "password123",
                    mock_settings
                )

                assert code is not None

                stored_username, stored_password, _ = _PENDING["test@example.com"]
                assert stored_username == "testuser"
                # Password should be hashed (not equal to original)
                assert stored_password != "password123"

        event_loop.run_until_complete(test())

    def test_create_pending_registration_email_sending_failure(self, mock_settings, event_loop):
        """Test that exception is raised if email sending fails."""
        async def test():
            with patch("asyncio.to_thread") as mock_thread:
                mock_thread.side_effect = Exception("SMTP error")

                with pytest.raises(Exception, match="SMTP error"):
                    await create_pending_registration(
                        "testuser",
                        "test@example.com",
                        "password123",
                        mock_settings
                    )

        event_loop.run_until_complete(test())

    def test_create_pending_registration_calls_send_email(self, mock_settings, event_loop):
        """Test that send_email_sync is called."""
        async def test():
            with patch("asyncio.to_thread") as mock_thread:
                mock_thread.return_value = None

                await create_pending_registration(
                    "testuser",
                    "test@example.com",
                    "password123",
                    mock_settings
                )

                mock_thread.assert_called_once()
                call_args = mock_thread.call_args[0]
                # First arg should be send_email_sync function
                assert call_args[0].__name__ == "send_email_sync"

        event_loop.run_until_complete(test())

    def test_create_pending_registration_code_format(self, mock_settings, event_loop):
        """Test that returned code has correct format."""
        async def test():
            with patch("asyncio.to_thread") as mock_thread:
                mock_thread.return_value = None

                code = await create_pending_registration(
                    "testuser",
                    "test@example.com",
                    "password123",
                    mock_settings
                )

                assert len(code) == 6
                assert code.isdigit()
                assert 0 <= int(code) <= 999999

        event_loop.run_until_complete(test())
