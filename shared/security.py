from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone
from pydantic import SecretStr


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_jwt_token(
    subject: str,
    secret: SecretStr | str,
    algorithm: str = "HS256",
    expires_minutes: int = 30
) -> str:
    payload = {
        "sub": subject,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_minutes),
        "iat": datetime.now(timezone.utc),
    }
    secret_value = secret.get_secret_value() if isinstance(secret, SecretStr) else secret
    return jwt.encode(payload, secret_value, algorithm=algorithm)

def decode_jwt_token(
    token: str,
    secret: SecretStr | str,
    algorithm: str = "HS256"
) -> dict:
    secret_value = secret.get_secret_value() if isinstance(secret, SecretStr) else secret
    return jwt.decode(token, secret_value, algorithms=[algorithm])