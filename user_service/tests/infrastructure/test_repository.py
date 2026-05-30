from uuid import uuid4

import pytest

from src.domain.entities import User
from src.domain.exceptions import UserNotFoundError, UserAlreadyExistsError
from src.infrastructure.repositories import UserRepositoryImpl
from src.infrastructure.database.uow import UnitOfWorkImpl
from src.infrastructure.database.manager import Base


class TestUserRepository:
    async def test_create_and_get_by_id(
        self, repository: UserRepositoryImpl, uow: UnitOfWorkImpl,
    ) -> None:
        user = User(id=uuid4(), username="repo_user", email="repo@example.com", hashed_password="hash")
        created = await repository.create(user)
        await uow.commit()

        assert created.id == user.id
        assert created.username == "repo_user"

        fetched = await repository.get_by_id(user.id)
        assert fetched is not None
        assert fetched.username == "repo_user"

    async def test_get_by_id_not_found(
        self, repository: UserRepositoryImpl,
    ) -> None:
        with pytest.raises(UserNotFoundError):
            await repository.get_by_id(uuid4())

    async def test_get_by_username(
        self, repository: UserRepositoryImpl, uow: UnitOfWorkImpl,
    ) -> None:
        user = User(id=uuid4(), username="findme", email="find@example.com", hashed_password="hash")
        await repository.create(user)
        await uow.commit()

        found = await repository.get_by_username("findme")
        assert found is not None
        assert found.id == user.id

        not_found = await repository.get_by_username("nope")
        assert not_found is None

    async def test_get_by_email(
        self, repository: UserRepositoryImpl, uow: UnitOfWorkImpl,
    ) -> None:
        user = User(id=uuid4(), username="email_test", email="unique@example.com", hashed_password="hash")
        await repository.create(user)
        await uow.commit()

        found = await repository.get_by_email("unique@example.com")
        assert found is not None
        assert found.id == user.id

        not_found = await repository.get_by_email("missing@example.com")
        assert not_found is None

    async def test_get_all(
        self, repository: UserRepositoryImpl, uow: UnitOfWorkImpl,
    ) -> None:
        for i in range(5):
            user = User(
                id=uuid4(),
                username=f"list_user_{i}",
                email=f"list{i}@example.com",
                hashed_password="hash",
            )
            await repository.create(user)
        await uow.commit()

        all_users = await repository.get_all(skip=0, limit=100)
        assert len(all_users) >= 5

        paginated = await repository.get_all(skip=2, limit=2)
        assert len(paginated) <= 2

    async def test_update_user(
        self, repository: UserRepositoryImpl, uow: UnitOfWorkImpl,
    ) -> None:
        user = User(id=uuid4(), username="before", email="before@example.com", hashed_password="hash")
        await repository.create(user)
        await uow.commit()

        user.username = "after"
        user.email = "after@example.com"
        await repository.update(user)
        await uow.commit()

        updated = await repository.get_by_id(user.id)
        assert updated.username == "after"
        assert updated.email == "after@example.com"

    async def test_update_not_found(
        self, repository: UserRepositoryImpl,
    ) -> None:
        user = User(id=uuid4(), username="ghost", email="ghost@example.com", hashed_password="hash")
        with pytest.raises(UserNotFoundError):
            await repository.update(user)

    async def test_delete_user(
        self, repository: UserRepositoryImpl, uow: UnitOfWorkImpl,
    ) -> None:
        user = User(id=uuid4(), username="delete_me", email="delete@example.com", hashed_password="hash")
        await repository.create(user)
        await uow.commit()

        result = await repository.delete(user.id)
        await uow.commit()
        assert result is True

        with pytest.raises(UserNotFoundError):
            await repository.get_by_id(user.id)

    async def test_delete_not_found(
        self, repository: UserRepositoryImpl,
    ) -> None:
        with pytest.raises(UserNotFoundError):
            await repository.delete(uuid4())

    async def test_duplicate_username(
        self, repository: UserRepositoryImpl, uow: UnitOfWorkImpl,
    ) -> None:
        uid1 = uuid4()
        uid2 = uuid4()
        user1 = User(id=uid1, username="duplicate_user", email="first@example.com", hashed_password="hash")
        await repository.create(user1)
        await uow.commit()

        user2 = User(id=uid2, username="duplicate_user", email="second@example.com", hashed_password="hash")
        with pytest.raises(UserAlreadyExistsError):
            await repository.create(user2)

    async def test_duplicate_email(
        self, repository: UserRepositoryImpl, uow: UnitOfWorkImpl,
    ) -> None:
        uid1 = uuid4()
        uid2 = uuid4()
        user1 = User(id=uid1, username="unique1", email="dup_email@example.com", hashed_password="hash")
        await repository.create(user1)
        await uow.commit()

        user2 = User(id=uid2, username="unique2", email="dup_email@example.com", hashed_password="hash")
        with pytest.raises(UserAlreadyExistsError):
            await repository.create(user2)

    async def test_unique_constraint_violation(
        self, repository: UserRepositoryImpl, uow: UnitOfWorkImpl,
    ) -> None:
        user = User(id=uuid4(), username="unique_test", email="unique@test.com", hashed_password="hash")
        await repository.create(user)
        await uow.commit()

        duplicate = User(id=uuid4(), username="unique_test", email="other@test.com", hashed_password="hash")
        with pytest.raises(UserAlreadyExistsError) as exc:
            await repository.create(duplicate)
        assert exc.value.code == "USER_ALREADY_EXISTS"
        assert "username" in exc.value.message
