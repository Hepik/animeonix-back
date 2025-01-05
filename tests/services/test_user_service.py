import pytest
from fastapi import HTTPException, status
from unittest.mock import MagicMock
from models.user import RoleEnum, Users
from repository.user_repository import UserRepository
from service.user_service import UserService

@pytest.fixture
def mock_user_repository():
    service = MagicMock(spec=UserRepository)
    return service

def test_get_users_by_username(mock_user_repository):
    page = 1
    limit = 10
    username = "testuser"
    mock_user = Users(**{
        "id": 1,
        "username": username,
        "email": "updateduser@example.com",
        "role": RoleEnum.user,
        "hashed_password": "password",
        "isActive": True,
        "avatar": "/static/avatars/default.jpg",
    })
    mock_user_repository.filter_users_by_username.return_value = mock_user
    mock_user_repository.get_filtered_count.return_value = 1

    service = UserService(mock_user_repository)
    result = service.get_users(**{
        "username": username,
        "page": page,
        "limit": limit,
        "id": None
    })

    assert result != None
    assert str(type(result)) == "<class 'dict'>"
    assert result.get("users") != None
    assert result["users"].username == mock_user.username
    assert result.get("total") == 1
    assert result.get("page") == page
    assert result.get("limit") == limit


def test_get_users_by_id(mock_user_repository):
    page = 1
    limit = 10
    id = 1
    mock_user = Users(**{
        "id": 1,
        "username": "testuser",
        "email": "updateduser@example.com",
        "role": RoleEnum.user,
        "hashed_password": "password",
        "isActive": True,
        "avatar": "/static/avatars/default.jpg",
    })
    mock_user_repository.get_user_by_id.return_value = mock_user

    service = UserService(mock_user_repository)
    result = service.get_users(**{
        "username": None,
        "page": page,
        "limit": limit,
        "id": id
    })

    assert result != None
    assert str(type(result)) == "<class 'dict'>"
    assert result.get("users") != None
    assert len(result["users"]) == 1
    assert result["users"][0].id == mock_user.id
    assert result.get("total") == 1
    assert result.get("page") == page
    assert result.get("limit") == limit


def test_get_users(mock_user_repository):
    page = 1
    limit = 2
    total = 1000
    mock_user_1 = Users(**{
        "id": 1,
        "username": "testuser",
        "email": "updateduser@example.com",
        "role": RoleEnum.user,
        "hashed_password": "password",
        "isActive": True,
        "avatar": "/static/avatars/default.jpg",
    })
    mock_user_2 = Users(**{
        "id": 2,
        "username": "testuser2",
        "email": "updateduser2@example.com",
        "role": RoleEnum.user,
        "hashed_password": "password",
        "isActive": True,
        "avatar": "/static/avatars/default.jpg",
    })
    mock_user_repository.get_users.return_value = [mock_user_1, mock_user_2]
    mock_user_repository.get_users_count.return_value = total

    service = UserService(mock_user_repository)
    result = service.get_users(**{
        "username": None,
        "page": page,
        "limit": limit,
        "id": None
    })

    assert result != None
    assert str(type(result)) == "<class 'dict'>"
    assert result.get("users") != None
    assert len(result["users"]) == 2
    assert result.get("total") == total
    assert result.get("page") == page
    assert result.get("limit") == limit


def test_get_user_by_email(mock_user_repository):
    email = "testuser@example.com"
    mock_user = Users(**{
        "id": 1,
        "username": "testuser",
        "email": email,
        "role": RoleEnum.user,
        "hashed_password": "password",
        "isActive": True,
        "avatar": "/static/avatars/default.jpg",
    })
    mock_user_repository.get_user_by_email.return_value = mock_user

    service = UserService(mock_user_repository)
    result = service.get_user_by_email(email)

    assert result is not None
    assert result.email == email
    assert result.username == mock_user.username
    assert result.id == mock_user.id


def test_delete_user_success(mock_user_repository):
    user_id = 1
    mock_user_repository.delete_by_id.return_value = True

    service = UserService(mock_user_repository)
    result = service.delete_user(user_id)

    assert result == {"detail": "User deleted successfully"}
    mock_user_repository.delete_by_id.assert_called_once_with(id=user_id)


def test_delete_user_not_found(mock_user_repository):
    user_id = 99
    mock_user_repository.delete_by_id.return_value = False

    service = UserService(mock_user_repository)
    
    with pytest.raises(HTTPException) as exc_info:
        service.delete_user(user_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"
    mock_user_repository.delete_by_id.assert_called_once_with(id=user_id)
