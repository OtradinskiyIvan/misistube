
from ..domain.entities import User
from .schemas import UserCreateDTO, UserResponseDTO, UserUpdateDTO


def map_create_dto(dto: UserCreateDTO) -> dict:
    return {
        "username": dto.username,
        "email": dto.email,
        "password": dto.password,
    }


def map_update_dto(dto: UserUpdateDTO) -> dict:
    result: dict = {}
    if dto.username is not None:
        result["username"] = dto.username
    if dto.email is not None:
        result["email"] = dto.email
    if dto.password is not None:
        result["password"] = dto.password
    if dto.status is not None:
        result["status"] = dto.status
    return result


def map_user_to_response(user: User) -> UserResponseDTO:
    return UserResponseDTO(
        id=user.id,
        username=user.username,
        email=user.email,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def map_users_to_response(users: list[User]) -> list[UserResponseDTO]:
    return [map_user_to_response(u) for u in users]
