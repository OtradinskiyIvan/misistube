import hashlib
import secrets

from ..domain.exceptions import InvalidUserDataError


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}${pwd_hash.hex()}"


def verify_password(password: str, stored: str) -> bool:
    salt, pwd_hash = stored.split("$", 1)
    computed = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 100_000,
    )
    return computed.hex() == pwd_hash


def validate_username(username: str) -> None:
    if not username or len(username) < 3:
        raise InvalidUserDataError("Username must be at least 3 characters long")
    if len(username) > 255:
        raise InvalidUserDataError("Username must not exceed 255 characters")
    if not username.isalnum() and not all(c.isalnum() or c in "_-" for c in username):
        raise InvalidUserDataError(
            "Username can only contain alphanumeric characters, underscores, and hyphens",
        )


def validate_email(email: str) -> None:
    if not email or "@" not in email:
        raise InvalidUserDataError("Invalid email format")
    if len(email) > 255:
        raise InvalidUserDataError("Email must not exceed 255 characters")


def validate_password(password: str) -> None:
    if not password or len(password) < 8:
        raise InvalidUserDataError("Password must be at least 8 characters long")
    if len(password) > 128:
        raise InvalidUserDataError("Password must not exceed 128 characters")
