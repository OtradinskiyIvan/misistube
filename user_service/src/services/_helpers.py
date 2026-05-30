import hashlib
import secrets


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
