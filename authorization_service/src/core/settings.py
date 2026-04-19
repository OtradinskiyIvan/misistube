from pydantic import SecretStr, field_validator
from shared.config import BaseSettings

class AuthSettings(BaseSettings):
    APP_NAME: str = "Authorization Service"
    JWT_SECRET: SecretStr
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret(cls, v: SecretStr) -> SecretStr:
        if len(v.get_secret_value()) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        return v