"""Domain exceptions for User Service."""
import sys
from pathlib import Path

ROOT_DIRECTORY = Path(__file__).resolve().parents[3]
if str(ROOT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ROOT_DIRECTORY))

from shared.exceptions import AppBaseError, ValidationAppError


class UserNotFoundError(AppBaseError):
    """Raised when a user is not found."""

    def __init__(self, user_id: str = ""):
        message = f"User not found" if not user_id else f"User with id {user_id} not found"
        super().__init__(message, code="USER_NOT_FOUND", status_code=404)


class UserAlreadyExistsError(ValidationAppError):
    """Raised when trying to create a user that already exists."""

    def __init__(self, field: str, value: str):
        message = f"User with {field} '{value}' already exists"
        super().__init__(message, code="USER_ALREADY_EXISTS")


class InvalidUserDataError(ValidationAppError):
    """Raised when user data is invalid."""

    def __init__(self, message: str):
        super().__init__(message, code="INVALID_USER_DATA")


class UserDeletionError(AppBaseError):
    """Raised when user deletion fails."""

    def __init__(self, message: str = "Failed to delete user"):
        super().__init__(message, code="USER_DELETION_FAILED", status_code=500)
