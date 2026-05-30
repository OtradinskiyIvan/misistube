import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from ..src.domain.entities.user import User
from ..src.infrastructure.database.models import UserModel
from ..src.infrastructure.repositories import UserRepository


class TestUserRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_session = MagicMock(spec=AsyncSession)
        self.mock_session.execute = AsyncMock()
        self.mock_session.commit = AsyncMock()
        self.mock_session.flush = AsyncMock()
        self.mock_session.refresh = AsyncMock()
        self.repo = UserRepository(self.mock_session)

    async def test_get_by_id_success(self):
        # Arrange
        user_id = uuid4()
        model = UserModel(
            id=user_id,
            email="test@example.com",
            hashed_password="hashed",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = model
        self.mock_session.execute.return_value = mock_result

        # Act
        result = await self.repo.get_by_id(user_id)

        # Assert
        self.assertIsInstance(result, User)
        self.assertEqual(result.id, user_id)
        self.assertEqual(result.email, "test@example.com")

    async def test_get_by_id_not_found(self):
        # Arrange
        user_id = uuid4()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_session.execute.return_value = mock_result

        # Act
        result = await self.repo.get_by_id(user_id)

        # Assert
        self.assertIsNone(result)

    async def test_get_by_email_success(self):
        # Arrange
        email = "test@example.com"
        user_id = uuid4()
        model = UserModel(
            id=user_id,
            email=email,
            hashed_password="hashed",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = model
        self.mock_session.execute.return_value = mock_result

        # Act
        result = await self.repo.get_by_email(email)

        # Assert
        self.assertIsInstance(result, User)
        self.assertEqual(result.email, email)

    async def test_save_success(self):
        # Arrange
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True
        )

        # Mock the model creation and database operations
        saved_model = UserModel(
            id=uuid4(),  # DB generates new ID
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.mock_session.add = MagicMock()

        # Mock the refresh to update the model
        def refresh_side_effect(model):
            model.id = saved_model.id
            model.created_at = saved_model.created_at
            model.updated_at = saved_model.updated_at

        self.mock_session.refresh.side_effect = refresh_side_effect

        # Act
        result = await self.repo.save(user)

        # Assert
        self.assertIsInstance(result, User)
        self.assertEqual(result.email, user.email)
        self.assertEqual(result.hashed_password, user.hashed_password)
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        self.mock_session.refresh.assert_called_once()

    async def test_exists_by_email_true(self):
        # Arrange
        email = "existing@example.com"
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = uuid4()  # Some ID exists
        self.mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await self.repo.exists_by_email(email)

        # Assert
        self.assertTrue(result)

    async def test_exists_by_email_false(self):
        # Arrange
        email = "nonexistent@example.com"
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await self.repo.exists_by_email(email)

        # Assert
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
