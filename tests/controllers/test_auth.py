import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import timedelta
from main import app
from service.user_service import UserService
from models.user import Users, RoleEnum


MOCK_USER = Users(**{
    "id": 1,
    "username": "testuser",
    "email": "testuser@example.com",
    "role": RoleEnum.user,
    "hashed_password": "$2b$12$xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "isActive": True,
    "avatar": "/static/avatars/default.jpg",
})

MOCK_INACTIVE_USER = Users(**{
    "id": 2,
    "username": "inactiveuser",
    "email": "inactiveuser@example.com",
    "role": RoleEnum.user,
    "hashed_password": "$2b$12$xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "isActive": False,
    "avatar": "/static/avatars/default.jpg",
})

MOCK_TOKEN = "mock.jwt.token"

client = TestClient(app)

@pytest.fixture
def mock_user_service():
    service = MagicMock(spec=UserService)
    return service

@pytest.fixture
def override_dependencies(mock_user_service):
    app.dependency_overrides[UserService] = lambda: mock_user_service
    yield
    app.dependency_overrides = {}

def test_login_success(mock_user_service, override_dependencies):
    mock_user_service.authenticate_user.return_value = MOCK_USER
    mock_user_service.create_access_token.return_value = MOCK_TOKEN

    response = client.post(
        "/auth/token",
        data={"username": MOCK_USER.username, "password": "correctpassword"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"access_token": MOCK_TOKEN, "token_type": "bearer"}
    mock_user_service.authenticate_user.assert_called_once_with(MOCK_USER.username, "correctpassword")
    mock_user_service.create_access_token.assert_called_once_with(MOCK_USER.id, MOCK_USER.role, timedelta(hours=12))


def test_login_invalid_credentials(mock_user_service, override_dependencies):
    mock_user_service.authenticate_user.return_value = False

    response = client.post(
        "/auth/token",
        data={"username": "wronguser", "password": "wrongpassword"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Wrong user or password."}
    mock_user_service.authenticate_user.assert_called_once_with("wronguser", "wrongpassword")
    mock_user_service.create_access_token.assert_not_called()


def test_login_inactive_user(mock_user_service, override_dependencies):
    mock_user_service.authenticate_user.return_value = MOCK_INACTIVE_USER

    response = client.post(
        "/auth/token",
        data={"username": MOCK_INACTIVE_USER.username, "password": "correctpassword"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "User is no activated. Please check your email."}
    mock_user_service.authenticate_user.assert_called_once_with(MOCK_INACTIVE_USER.username, "correctpassword")
    mock_user_service.create_access_token.assert_not_called()
