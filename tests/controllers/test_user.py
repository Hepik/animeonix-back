import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from io import BytesIO
from main import app
from models.user import Users
from schemas.user_schema import *
from service.user_service import UserService
from service.email_service import EmailService
from service.file_service import FileService
from controllers.user import router
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta
from models.user import RoleEnum


MOCK_TOKEN = 'mock_token'

MOCK_ADMIN = Users(**{
        "id": 4,
        "username": "admin",
        "email": "admin@example.com",
        "role": RoleEnum.admin,
        "hashed_password": "password",
        "isActive": True,
        "avatar": "/static/avatars/default.jpg",
    })

app.include_router(router)

client = TestClient(app)


@pytest.fixture
def mock_user_service():
    service = MagicMock(spec=UserService)
    return service

@pytest.fixture
def mock_email_service():
    service = MagicMock(spec=EmailService)
    return service

@pytest.fixture
def mock_oauth2_bearer():
    def fake_oauth2_bearer():
        return MOCK_TOKEN
    return fake_oauth2_bearer

@pytest.fixture
def mock_file_service():
    service = MagicMock(spec=FileService)
    return service

@pytest.fixture
def override_dependencies(mock_user_service, mock_email_service, mock_file_service):
    app.dependency_overrides[UserService] = lambda: mock_user_service
    app.dependency_overrides[EmailService] = lambda: mock_email_service
    app.dependency_overrides[FileService] = lambda: mock_file_service
    app.dependency_overrides[OAuth2PasswordBearer] = lambda: mock_oauth2_bearer
    yield
    app.dependency_overrides = {}


def test_get_users_success(mock_user_service, override_dependencies):
    mock_response = {
        "users": [
            {"id": 1, "username": "testuser1", "email": "test1@example.com", "role": "admin", "isActive": True, "avatar": "test"},
            {"id": 2, "username": "testuser2", "email": "test2@example.com", "role": "admin", "isActive": True, "avatar": "test"},
        ],
        "total": 2,
        "page": 1,
        "limit": 10,
    }
    mock_user_service.get_users.return_value = mock_response

    response = client.get("/users?page=1&limit=10")

    assert response.status_code == 200
    assert response.json() == mock_response
    mock_user_service.get_users.assert_called_once_with(1, 10, "", None)


def test_get_users_with_username_filter(mock_user_service, override_dependencies):
    username = "testuser"
    mock_response = {
        "users": [
            {"id": 1, "username": "testuser", "email": "testuser@example.com", "role": "admin", "isActive": True, "avatar": "test"},
        ],
        "total": 1,
        "page": 1,
        "limit": 10,
    }
    mock_user_service.get_users.return_value = mock_response

    response = client.get(f"/users?username={username}")

    assert response.status_code == 200
    assert response.json() == mock_response
    mock_user_service.get_users.assert_called_once_with(1, 10, username, None)


def test_get_users_with_id_filter(mock_user_service, override_dependencies):
    user_id = 1
    mock_response = {
        "users": [
            {"id": 1, "username": "testuser", "email": "testuser@example.com", "role": "admin", "isActive": True, "avatar": "test"},
        ],
        "total": 1,
        "page": 1,
        "limit": 10,
    }
    mock_user_service.get_users.return_value = mock_response

    response = client.get(f"/users?id={user_id}")

    assert response.status_code == 200
    assert response.json() == mock_response
    mock_user_service.get_users.assert_called_once_with(1, 10, "", user_id)


def test_oauth2_bearer_user_valid_token(mock_user_service, override_dependencies):
    mock_user = {
        "id": 1,
        "username": "testuser",
        "email": "testuser@example.com",
        "role": "admin",
        "isActive": True,
        "avatar": "test",
    }

    mock_user_service.get_current_user.return_value = mock_user

    response = client.get("/users/current", headers={"Authorization": f"Bearer {MOCK_TOKEN}"})

    assert response.status_code == 200
    assert response.json() == mock_user
    mock_user_service.get_current_user.assert_called_once_with(MOCK_TOKEN)


def test_oauth2_bearer_no_user(mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = None

    response = client.get("/users/current", headers={"Authorization": "Bearer invalid_token"})

    assert response.status_code == 403
    assert response.json() == {"detail": "Access denied. Authentication required."}


def test_oauth2_bearer_user_missing_token(mock_user_service, override_dependencies):
    response = client.get("/users/current")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_register_user_success(mock_user_service, mock_email_service, override_dependencies):
    mock_user_data = {
        "id": 1,
        "username": "testuser",
        "email": "testuser@example.com",
        "hashed_password": "securepassword123",
        "role": "user",
        "isActive": False,
        "avatar": "avatar",
    }
    mock_user = Users(**mock_user_data)
    mock_user_service.register_user.return_value = mock_user
    mock_email_service.create_user_activation_token.return_value = "mock_activation_token"

    response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 200
    mock_user_service.register_user.assert_called_once_with(
        RegisterUserRequest(username="testuser", email="testuser@example.com", password="securepassword123")
    )
    mock_email_service.create_user_activation_token.assert_called_once_with(1, timedelta(days=256 * 365))
    mock_email_service.send_email.assert_called_once_with(
        "mock_activation_token",
        recipient_email="testuser@example.com",
        recipient_username="testuser",
    )


def test_register_user_email_failure(mock_user_service, mock_email_service, override_dependencies):
    mock_user_data = {
        "id": 1,
        "username": "testuser",
        "email": "testuser@example.com",
        "hashed_password": "securepassword123",
        "role": "user",
        "isActive": False,
        "avatar": "avatar",
    }
    mock_user = Users(**mock_user_data)
    mock_user_service.register_user.return_value = mock_user
    mock_email_service.create_user_activation_token.return_value = "mock_activation_token"
    mock_email_service.send_email.side_effect = Exception("Email sending failed")

    response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Could not send an email."}
    mock_user_service.register_user.assert_called_once_with(
        RegisterUserRequest(username="testuser", email="testuser@example.com", password="securepassword123")
    )
    mock_email_service.create_user_activation_token.assert_called_once_with(1, timedelta(days=256 * 365))
    mock_email_service.send_email.assert_called_once_with(
        "mock_activation_token",
        recipient_email="testuser@example.com",
        recipient_username="testuser",
    )
    mock_user_service.delete_user.assert_called_once_with(1)


def test_activation_token_verification_success(mock_email_service, override_dependencies):
    mock_email_service.check_activation_token.return_value = {
        "detail": "account activated successfully"
    }

    activation_token = "valid_token"

    response = client.post(
        "/users/account/activation",
        params={"activation_token": activation_token},
    )

    assert response.status_code == 200
    assert response.json() == {"detail": "account activated successfully"}
    mock_email_service.check_activation_token.assert_called_once_with(activation_token)


def test_activation_token_verification_expired_token(mock_email_service, override_dependencies):
    mock_email_service.check_activation_token.side_effect = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired."
    )

    activation_token = "expired_token"

    response = client.post(
        "/users/account/activation",
        params={"activation_token": activation_token},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Token has expired."}
    mock_email_service.check_activation_token.assert_called_once_with(activation_token)


def test_activation_token_verification_invalid_token(mock_email_service, override_dependencies):
    """Test account activation with an invalid token."""
    mock_email_service.check_activation_token.side_effect = HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Token is not valid."
    )

    activation_token = "invalid_token"

    response = client.post(
        "/users/account/activation",
        params={"activation_token": activation_token},
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Token is not valid."}
    mock_email_service.check_activation_token.assert_called_once_with(activation_token)


def test_send_email_reset_password_success(mock_user_service, mock_email_service, override_dependencies):
    mock_user = MagicMock(id=1, email="testuser@example.com", username="testuser")
    mock_user_service.get_user_by_email.return_value = mock_user
    mock_email_service.create_password_reset_token.return_value = "mock_reset_token"

    response = client.post(
        "/users/reset/password/email",
        params={"email": "testuser@example.com"},
    )

    assert response.status_code == 200
    mock_user_service.get_user_by_email.assert_called_once_with("testuser@example.com")
    mock_email_service.create_password_reset_token.assert_called_once_with(1, timedelta(hours=2))
    mock_email_service.send_reset_password_email.assert_called_once_with(
        "mock_reset_token", recipient_email="testuser@example.com", recipient_username="testuser"
    )


def test_send_email_reset_password_user_not_found(mock_user_service, override_dependencies):
    mock_user_service.get_user_by_email.return_value = None

    response = client.post(
        "/users/reset/password/email",
        params={"email": "unknown@example.com"},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Could not send an email."}
    mock_user_service.get_user_by_email.assert_called_once_with("unknown@example.com")


def test_send_email_reset_password_email_sending_error(mock_user_service, mock_email_service, override_dependencies):
    mock_user = MagicMock(id=1, email="testuser@example.com", username="testuser")
    mock_user_service.get_user_by_email.return_value = mock_user
    mock_email_service.create_password_reset_token.return_value = "mock_reset_token"
    mock_email_service.send_reset_password_email.side_effect = Exception("SMTP error")

    response = client.post(
        "/users/reset/password/email",
        params={"email": "testuser@example.com"},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Could not send an email."}
    mock_user_service.get_user_by_email.assert_called_once_with("testuser@example.com")
    mock_email_service.create_password_reset_token.assert_called_once_with(1, timedelta(hours=2))
    mock_email_service.send_reset_password_email.assert_called_once_with(
        "mock_reset_token", recipient_email="testuser@example.com", recipient_username="testuser"
    )


def test_reset_password_token_verification_success(mock_email_service, override_dependencies):
    mock_email_service.check_reset_password_token.return_value = 1

    reset_password_token = "valid_reset_token"

    response = client.post(
        "/users/reset/password/token/verification",
        params={"reset_password_token": reset_password_token},
    )

    assert response.status_code == 200
    assert response.json() == 1
    mock_email_service.check_reset_password_token.assert_called_once_with(reset_password_token)


def test_reset_password_token_verification_expired_token(mock_email_service, override_dependencies):
    mock_email_service.check_reset_password_token.side_effect = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired."
    )

    reset_password_token = "expired_reset_token"

    response = client.post(
        "/users/reset/password/token/verification",
        params={"reset_password_token": reset_password_token},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Token has expired."}
    mock_email_service.check_reset_password_token.assert_called_once_with(reset_password_token)


def test_reset_password_token_verification_invalid_token(mock_email_service, override_dependencies):
    mock_email_service.check_reset_password_token.side_effect = HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Token is not valid."
    )

    reset_password_token = "invalid_reset_token"

    response = client.post(
        "/users/reset/password/token/verification",
        params={"reset_password_token": reset_password_token},
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Token is not valid."}
    mock_email_service.check_reset_password_token.assert_called_once_with(reset_password_token)


def test_reset_password_success(mock_user_service, mock_email_service, override_dependencies):
    mock_user_id = 1
    mock_email_service.check_reset_password_token.return_value = mock_user_id

    response = client.post(
        "/users/reset/password",
        json={
            "reset_password_token": "valid_reset_token",
            "new_password": "new_secure_password"
        }
    )

    assert response.status_code == 200
    assert response.json() == {"detail": "password changed successfully"}

    mock_email_service.check_reset_password_token.assert_called_once_with("valid_reset_token")
    
    mock_user_service.reset_password.assert_called_once_with("new_secure_password", mock_user_id)


def test_reset_password_expired_token(mock_user_service, mock_email_service, override_dependencies):
    mock_email_service.check_reset_password_token.side_effect = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired."
    )

    response = client.post(
        "/users/reset/password",
        json={
            "reset_password_token": "expired_reset_token",
            "new_password": "new_secure_password"
        }
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Token has expired."}

    mock_email_service.check_reset_password_token.assert_called_once_with("expired_reset_token")


def test_reset_password_invalid_token(mock_user_service, mock_email_service, override_dependencies):
    mock_email_service.check_reset_password_token.side_effect = HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Token is not valid."
    )

    response = client.post(
        "/users/reset/password",
        json={
            "reset_password_token": "invalid_reset_token",
            "new_password": "new_secure_password"
        }
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Token is not valid."}

    mock_email_service.check_reset_password_token.assert_called_once_with("invalid_reset_token")


def test_reset_password_service_exception(mock_user_service, mock_email_service, override_dependencies):
    mock_user_id = 1
    mock_email_service.check_reset_password_token.return_value = mock_user_id

    mock_user_service.reset_password.side_effect = UserService.UserServiceException("Service error")

    response = client.post(
        "/users/reset/password",
        json={
            "reset_password_token": "valid_reset_token",
            "new_password": "new_secure_password"
        }
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Service error"}

    mock_email_service.check_reset_password_token.assert_called_once_with("valid_reset_token")
    mock_user_service.reset_password.assert_called_once_with("new_secure_password", mock_user_id)


def test_create_user_success(mock_user_service, override_dependencies):
    create_user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "securepassword123",
        "role": "user"
    }
    
    mock_user_service.create_user.return_value = None
    mock_user_service.get_current_user.return_value = MOCK_ADMIN

    headers = {"Authorization": f"Bearer {MOCK_TOKEN}"}
    response = client.post("/users", json=create_user_data, headers=headers)

    assert response.status_code == status.HTTP_201_CREATED
    mock_user_service.create_user.assert_called_once_with(CreateUserRequest(**{
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "securepassword123",
        "role": RoleEnum.user
    }))


def test_create_user_not_admin(mock_user_service, override_dependencies):
    create_user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "securepassword123",
        "role": "user"
    }
    
    mock_user_service.get_current_user.return_value = MagicMock(role=RoleEnum.user)
    headers = {"Authorization": f"Bearer {MOCK_TOKEN}"}
    response = client.post("/users", json=create_user_data, headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Access denied. Admin role required."}
    mock_user_service.create_user.assert_not_called()


def test_create_user_missing_auth(mock_user_service, override_dependencies):
    create_user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "securepassword123",
        "role": "user"
    }
    
    response = client.post("/users", json=create_user_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    mock_user_service.create_user.assert_not_called()


def test_create_user_failure(mock_user_service, override_dependencies):
    create_user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "securepassword123",
        "role": "user"
    }

    mock_user_service.create_user.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating user"
    )
    mock_user_service.get_current_user.return_value = MOCK_ADMIN

    headers = {"Authorization": f"Bearer {MOCK_TOKEN}"}
    response = client.post("/users", json=create_user_data, headers=headers)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"detail": "Error creating user"}
    mock_user_service.create_user.assert_called_once_with(CreateUserRequest(**{
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "securepassword123",
        "role": RoleEnum.user
    }))


def test_partial_update_user_success(mock_user_service, override_dependencies):
    user_id = 1
    update_data = {
        "username": "updateduser",
        "email": "updateduser@example.com",
        "role": "user",
        "isActive": True,
    }
    updated_user = Users(**{
        "id": user_id,
        "username": "updateduser",
        "email": "updateduser@example.com",
        "role": RoleEnum.user,
        "hashed_password": "password",
        "isActive": True,
        "avatar": "/static/avatars/default.jpg",
    })
    mock_user_service.get_current_user.return_value = MOCK_ADMIN
    mock_user_service.partial_update_user.return_value = updated_user

    headers = {"Authorization": f"Bearer {MOCK_TOKEN}"}
    response = client.patch(f"/users/{user_id}", json=update_data, headers=headers)

    assert response.status_code == 200
    content: dict = response.json()
    assert content.get("id") == updated_user.id
    assert content.get("username") == updated_user.username
    assert content.get("email") == updated_user.email
    assert content.get("role") == updated_user.role.value
    assert content.get("isActive") == updated_user.isActive
    assert content.get("avatar") == updated_user.avatar
    mock_user_service.partial_update_user.assert_called_once_with(
        id=user_id, user=UserUpdate(**{
        "username": "updateduser",
        "email": "updateduser@example.com",
        "role": RoleEnum.user,
        "isActive": True,
    })
    )


def test_partial_update_user_not_found(mock_user_service, override_dependencies):
    user_id = 99
    update_data = {
        "username": "nonexistentuser",
    }
    mock_user_service.get_current_user.return_value = MOCK_ADMIN
    mock_user_service.partial_update_user.side_effect = HTTPException(
        status_code=404, detail="User not found"
    )

    headers = {"Authorization": f"Bearer {MOCK_TOKEN}"}
    response = client.patch(f"/users/{user_id}", json=update_data, headers=headers)

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
    mock_user_service.partial_update_user.assert_called_once_with(
        id=user_id, user=UserUpdate(username="nonexistentuser")
    )


def test_partial_update_user_unauthorized(mock_user_service, override_dependencies):
    user_id = 1
    update_data = {
        "username": "unauthorizedupdate",
    }
    mock_user_service.get_current_user.return_value = MagicMock(role=RoleEnum.user)

    headers = {"Authorization": f"Bearer {MOCK_TOKEN}"}
    response = client.patch(f"/users/{user_id}", json=update_data, headers=headers)

    assert response.status_code == 403
    assert response.json() == {"detail": "Access denied. Admin role required."}
    mock_user_service.partial_update_user.assert_not_called()


def test_change_password_success(mock_user_service, override_dependencies):
    mock_user = MagicMock(id=1, username="testuser", hashed_password="old_hashed_password")
    mock_user_service.get_current_user.return_value = mock_user
    mock_user_service.change_password.return_value = None

    response = client.patch(
        "/users/change/password",
        json={"current_password": "old_password", "new_password": "new_secure_password"},
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )

    assert response.status_code == 200
    assert response.json() == {"detail": "password changed successfully"}
    mock_user_service.get_current_user.assert_called_once_with(MOCK_TOKEN)
    mock_user_service.change_password.assert_called_once_with(
        mock_user, current_password="old_password", new_password="new_secure_password"
    )


def test_change_password_incorrect_current_password(mock_user_service, override_dependencies):
    mock_user = MagicMock(id=1, username="testuser", hashed_password="old_hashed_password")
    mock_user_service.get_current_user.return_value = mock_user
    mock_user_service.change_password.side_effect = HTTPException(
        status_code=400, detail="Incorrect current password"
    )

    response = client.patch(
        "/users/change/password",
        json={"current_password": "wrong_password", "new_password": "new_secure_password"},
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect current password"}
    mock_user_service.get_current_user.assert_called_once_with(MOCK_TOKEN)
    mock_user_service.change_password.assert_called_once_with(
        mock_user, current_password="wrong_password", new_password="new_secure_password"
    )


def test_change_password_service_exception(mock_user_service, override_dependencies):
    mock_user = MagicMock(id=1, username="testuser", hashed_password="old_hashed_password")
    mock_user_service.get_current_user.return_value = mock_user
    mock_user_service.change_password.side_effect = UserService.UserServiceException("Unexpected error")

    response = client.patch(
        "/users/change/password",
        json={"current_password": "old_password", "new_password": "new_secure_password"},
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Unexpected error"}
    mock_user_service.get_current_user.assert_called_once_with(MOCK_TOKEN)
    mock_user_service.change_password.assert_called_once_with(
        mock_user, current_password="old_password", new_password="new_secure_password"
    )


def test_change_password_no_authentication(mock_user_service, override_dependencies):
    response = client.patch(
        "/users/change/password",
        json={"current_password": "old_password", "new_password": "new_secure_password"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_delete_user_success(mock_user_service, override_dependencies):
    mock_user_service.delete_user.return_value = {"detail": "User deleted successfully"}
    mock_user_service.get_current_user.return_value = MOCK_ADMIN
    headers = {"Authorization": f"Bearer {MOCK_TOKEN}"}

    response = client.delete("/users/1", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"detail": "User deleted successfully"}
    mock_user_service.delete_user.assert_called_once_with(id=1)

def test_delete_user_not_found(mock_user_service, override_dependencies):
    mock_user_service.delete_user.side_effect = HTTPException(status_code=404, detail="User not found")
    headers = {"Authorization": f"Bearer {MOCK_TOKEN}"}
    mock_user_service.get_current_user.return_value = MOCK_ADMIN

    response = client.delete("/users/999", headers=headers)

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
    mock_user_service.delete_user.assert_called_once_with(id=999)

def test_delete_user_access_denied(mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MagicMock(role=RoleEnum.user)
    headers = {"Authorization": "Bearer non_admin_token"}

    response = client.delete("/users/1", headers=headers)

    assert response.status_code == 403
    assert response.json() == {"detail": "Access denied. Admin role required."}

def test_delete_user_unauthenticated(mock_user_service, override_dependencies):
    response = client.delete("/users/1")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_upload_avatar_success(mock_user_service, mock_file_service, override_dependencies):
    file_content = BytesIO(b"fake_image_data")
    mock_file_service.process_avatar.return_value = MagicMock(avatar="/static/avatars/new_avatar.jpg")
    mock_user_service.get_current_user.return_value = MagicMock(id=1, avatar="/old/avatar.png")
    mock_user_service.partial_update_user.return_value = None

    response = client.post(
        "/users/change/avatar",
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"},
        files={"file": ("avatar.png", file_content, "image/png")},
    )

    assert response.status_code == 200
    assert response.json() == {"detail": "Avatar updated successfully", "filename": "/static/avatars/new_avatar.jpg"}
    mock_file_service.process_avatar.assert_called_once()
    mock_user_service.partial_update_user.assert_called_once_with(1, mock_file_service.process_avatar.return_value)

def test_upload_avatar_invalid_file_type(mock_user_service, mock_file_service, override_dependencies):
    file_content = BytesIO(b"fake_non_image_data")
    mock_file_service.process_avatar.side_effect = HTTPException(
        status_code=400, detail="Invalid file type. Only JPEG and PNG are allowed."
    )
    
    response = client.post(
        "/users/change/avatar",
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"},
        files={"file": ("avatar.txt", file_content, "text/plain")},
    )
    print("Response status:", response.status_code)
    print("Response data:", response.json())

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid file type. Only JPEG and PNG are allowed."}
    mock_file_service.process_avatar.assert_called_once()
    mock_user_service.partial_update_user.assert_not_called()

def test_upload_avatar_server_error(mock_user_service, mock_file_service, override_dependencies):
    file_content = BytesIO(b"fake_image_data")
    mock_file_service.process_avatar.side_effect = HTTPException(status_code=500, detail=f"Error uploading avatar")

    response = client.post(
        "/users/change/avatar",
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"},
        files={"file": ("avatar.png", file_content, "image/png")},
    )

    assert response.status_code == 500
    assert "Error uploading avatar" in response.json()["detail"]
    mock_file_service.process_avatar.assert_called_once()
    mock_user_service.partial_update_user.assert_not_called()

def test_upload_avatar_unauthorized():
    file_content = BytesIO(b"fake_image_data")

    response = client.post(
        "/users/change/avatar",
        files={"file": ("avatar.png", file_content, "image/png")},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
