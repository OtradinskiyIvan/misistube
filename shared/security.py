from typing import cast

from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone
from pydantic import SecretStr


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return cast(str, pwd_context.hash(password))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return cast(bool, pwd_context.verify(plain_password, hashed_password))

def create_jwt_token(
    subject: str,
    secret: SecretStr | str,
    algorithm: str = "HS256",
    expires_minutes: int = 30,
    **additional_claims
) -> str:
    payload = {
        "sub": subject,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_minutes),
        "iat": datetime.now(timezone.utc),
    }
    payload.update(additional_claims)
    secret_value = secret.get_secret_value() if isinstance(secret, SecretStr) else secret
    return jwt.encode(payload, secret_value, algorithm=algorithm)

def decode_jwt_token(
    token: str,
    secret: SecretStr | str,
    algorithm: str = "HS256"
) -> dict:
    secret_value = secret.get_secret_value() if isinstance(secret, SecretStr) else secret
    return jwt.decode(token, secret_value, algorithms=[algorithm])


async def get_token_payload(authorization: str, secret: SecretStr | str, algorithm: str = "HS256") -> dict:
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        from shared.exceptions import AuthenticationError
        raise AuthenticationError("Invalid authorization header")
    token = authorization[len(prefix):]
    try:
        return decode_jwt_token(token, secret, algorithm)
    except jwt.ExpiredSignatureError:
        from shared.exceptions import AuthenticationError
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        from shared.exceptions import AuthenticationError
        raise AuthenticationError("Invalid token")


async def require_role(role: str, payload: dict) -> None:
    roles = payload.get("roles", [])
    if role not in roles:
        from shared.exceptions import ForbiddenError
        raise ForbiddenError(f"Required role: {role}")