import unittest
from datetime import datetime
from uuid import uuid4

from authorization_service.src.presentations.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from pydantic import ValidationError


class TestAuthSchemas(unittest.TestCase):
    def test_register_request_valid(self):
        # Arrange
        data = {
            "email": "test@example.com",
            "password": "password123"
        }

        # Act
        request = RegisterRequest(**data)

        # Assert
        self.assertEqual(request.email, "test@example.com")
        self.assertEqual(request.password, "password123")

    def test_register_request_invalid_email(self):
        # Arrange
        data = {
            "email": "invalid-email",
            "password": "password123"
        }

        # Act & Assert
        with self.assertRaises(ValidationError):
            RegisterRequest(**data)

    def test_register_request_password_too_short(self):
        # Arrange
        data = {
            "email": "test@example.com",
            "password": "short"
        }

        # Act & Assert
        with self.assertRaises(ValidationError):
            RegisterRequest(**data)

    def test_register_request_password_too_long(self):
        # Arrange
        data = {
            "email": "test@example.com",
            "password": "a" * 129  # 129 characters
        }

        # Act & Assert
        with self.assertRaises(ValidationError):
            RegisterRequest(**data)

    def test_login_request_valid(self):
        # Arrange
        data = {
            "email": "test@example.com",
            "password": "password123"
        }

        # Act
        request = LoginRequest(**data)

        # Assert
        self.assertEqual(request.email, "test@example.com")
        self.assertEqual(request.password, "password123")

    def test_token_response_valid(self):
        # Arrange
        data = {
            "access_token": "access_token_here",
            "refresh_token": "refresh_token_here"
        }

        # Act
        response = TokenResponse(**data)

        # Assert
        self.assertEqual(response.access_token, "access_token_here")
        self.assertEqual(response.refresh_token, "refresh_token_here")
        self.assertEqual(response.token_type, "Bearer")  # Default value

    def test_token_response_custom_token_type(self):
        # Arrange
        data = {
            "access_token": "access_token_here",
            "refresh_token": "refresh_token_here",
            "token_type": "Custom"
        }

        # Act
        response = TokenResponse(**data)

        # Assert
        self.assertEqual(response.token_type, "Custom")

    def test_user_out_valid(self):
        # Arrange
        user_id = uuid4()
        created_at = datetime.now()
        data = {
            "id": user_id,
            "email": "test@example.com",
            "is_active": True,
            "created_at": created_at
        }

        # Act
        user_out = UserOut(**data)

        # Assert
        self.assertEqual(user_out.id, user_id)
        self.assertEqual(user_out.email, "test@example.com")
        self.assertTrue(user_out.is_active)
        self.assertEqual(user_out.created_at, created_at)

    def test_user_out_from_attributes(self):
        # Arrange: Simulate SQLAlchemy model
        class MockUser:
            def __init__(self):
                self.id = uuid4()
                self.email = "test@example.com"
                self.is_active = True
                self.created_at = datetime.now()

        mock_user = MockUser()

        # Act
        user_out = UserOut.model_validate(mock_user)

        # Assert
        self.assertEqual(user_out.id, mock_user.id)
        self.assertEqual(user_out.email, mock_user.email)
        self.assertTrue(user_out.is_active)


if __name__ == "__main__":
    unittest.main()
