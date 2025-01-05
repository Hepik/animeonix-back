import pytest
from fastapi import HTTPException, status
from unittest.mock import MagicMock
from models.user import RoleEnum, Users
from repository.user_repository import UserRepository
from service.user_service import UserService
from config.database import get_db
from sqlalchemy.orm import Session, Query


MOCK_USER = Users(**{
        "id": 4,
        "username": "testuser",
        "email": "testuser@example.com",
        "role": RoleEnum.user,
        "hashed_password": "password",
        "isActive": True,
        "avatar": "/static/avatars/default.jpg",
    })


@pytest.fixture
def mock_db_query():
    query = MagicMock(spec=Query)
    return query


@pytest.fixture
def mock_db_session():
    session = MagicMock(spec=Session)
    return session


def test_get_users(mock_db_session, mock_db_query):
    skip = 2
    limit = 5

    mock_db_session.query.return_value = mock_db_query

    mock_db_query.offset.return_value = mock_db_query
    mock_db_query.limit.return_value = mock_db_query
    mock_db_query.all.return_value = [MOCK_USER]

    repository = UserRepository(mock_db_session)
    response = repository.get_users(skip, limit)

    assert response != None
    assert len(response) == 1
    assert response[0] == MOCK_USER
    mock_db_query.offset.assert_called_once_with(skip)
    mock_db_query.limit.assert_called_once_with(limit)


def test_get_users_count(mock_db_session, mock_db_query):
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.count.return_value = 10

    repository = UserRepository(mock_db_session)
    result = repository.get_users_count()

    assert result == 10
    mock_db_query.count.assert_called_once()


def test_filter_users_by_username(mock_db_session, mock_db_query):
    username = "test"
    skip = 1
    limit = 5

    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.offset.return_value = mock_db_query
    mock_db_query.limit.return_value = mock_db_query
    mock_db_query.all.return_value = [MOCK_USER]

    repository = UserRepository(mock_db_session)
    result = repository.filter_users_by_username(username, skip, limit)

    assert result == [MOCK_USER]
    mock_db_query.filter.assert_called_once()
    mock_db_query.offset.assert_called_once_with(skip)
    mock_db_query.limit.assert_called_once_with(limit)


def test_get_filtered_count(mock_db_session, mock_db_query):
    username = "test"

    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.count.return_value = 5

    repository = UserRepository(mock_db_session)
    result = repository.get_filtered_count(username)

    assert result == 5
    mock_db_query.filter.assert_called_once()
    mock_db_query.count.assert_called_once()


def test_get_user_by_username(mock_db_session, mock_db_query):
    username = "testuser"

    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.first.return_value = MOCK_USER

    repository = UserRepository(mock_db_session)
    result = repository.get_user_by_username(username)

    assert result == MOCK_USER
    mock_db_query.filter.assert_called_once()
    mock_db_query.first.assert_called_once()


def test_get_user_by_id(mock_db_session, mock_db_query):
    user_id = 4

    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.first.return_value = MOCK_USER

    repository = UserRepository(mock_db_session)
    result = repository.get_user_by_id(user_id)

    assert result == MOCK_USER
    mock_db_query.filter.assert_called_once()
    mock_db_query.first.assert_called_once()


def test_get_user_by_email(mock_db_session, mock_db_query):
    email = "testuser@example.com"

    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.first.return_value = MOCK_USER

    repository = UserRepository(mock_db_session)
    result = repository.get_user_by_email(email)

    assert result == MOCK_USER
    mock_db_query.filter.assert_called_once()
    mock_db_query.first.assert_called_once()


def test_create_user(mock_db_session, mock_db_query):
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "hashed_password": "hashed_password",
        "role": RoleEnum.user,
    }
    created_user = Users(**user_data)

    mock_db_session.query.return_value = mock_db_query
    mock_db_session.add.return_value = mock_db_query
    mock_db_session.commit.return_value = mock_db_query
    mock_db_session.refresh.return_value = created_user

    repository = UserRepository(mock_db_session)
    result = repository.create_user(user_data)

    assert result.username == user_data["username"]
    assert result.email == user_data["email"]
    assert result.role == user_data["role"]
    mock_db_session.add.assert_called_once_with(result)
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(result)


def test_update_user(mock_db_session, mock_db_query):
    db_user = MOCK_USER

    mock_db_session.query.return_value = mock_db_query
    mock_db_session.commit.return_value = mock_db_query
    mock_db_session.refresh.return_value = db_user

    repository = UserRepository(mock_db_session)
    result = repository.update_user(db_user)

    assert result is True
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(db_user)


def test_partial_update_user(mock_db_session, mock_db_query):
    user_id = 4
    user_data = {"email": "updated@example.com"}
    updated_user = Users(**{
        "id": user_id,
        "username": "testuser",
        "email": "updated@example.com",
        "hashed_password": "hashed_password",
        "role": RoleEnum.user,
        "isActive": True,
        "avatar": "/static/avatars/default.jpg",
    })

    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.first.return_value = MOCK_USER
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = updated_user

    repository = UserRepository(mock_db_session)
    result = repository.partial_update_user(user_id, user_data)

    assert result != None
    assert result.email == updated_user.email
    assert result.username == MOCK_USER.username
    assert result.role == MOCK_USER.role
    mock_db_query.filter.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()


def test_activate_user_profile(mock_db_session, mock_db_query):
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.first.return_value = MOCK_USER
    mock_db_session.commit.return_value = mock_db_query
    mock_db_session.refresh.return_value = MOCK_USER

    repository = UserRepository(mock_db_session)
    repository.activate_user_profile(MOCK_USER.id)

    assert MOCK_USER.isActive is True
    mock_db_query.filter.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(MOCK_USER)


def test_reset_password(mock_db_session, mock_db_query):
    hashed_password = "new_hashed_password"

    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.first.return_value = MOCK_USER
    mock_db_session.commit.return_value = mock_db_query
    mock_db_session.refresh.return_value = MOCK_USER

    repository = UserRepository(mock_db_session)
    repository.reset_password(hashed_password, MOCK_USER.id)

    assert MOCK_USER.hashed_password == hashed_password
    mock_db_query.filter.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(MOCK_USER)


def test_delete_by_id(mock_db_session, mock_db_query):
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.first.return_value = MOCK_USER
    mock_db_session.delete.return_value = mock_db_query
    mock_db_session.commit.return_value = mock_db_query

    repository = UserRepository(mock_db_session)
    result = repository.delete_by_id(MOCK_USER.id)

    assert result is True
    mock_db_query.filter.assert_called_once()
    mock_db_session.delete.assert_called_once_with(MOCK_USER)
    mock_db_session.commit.assert_called_once()


def test_delete_by_id_not_found(mock_db_session, mock_db_query):
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.first.return_value = None

    repository = UserRepository(mock_db_session)
    result = repository.delete_by_id(999)

    assert result is False
    mock_db_query.filter.assert_called_once()
    mock_db_session.commit.assert_not_called()
