import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from io import BytesIO
from main import app
from models.title import Title
from schemas.title_schema import *
from service.title_service import TitleService
from service.file_service import FileService
from service.user_service import UserService
from controllers.title import router
from fastapi.security import OAuth2PasswordBearer
from models.user import RoleEnum
from models.user import Users


MOCK_TOKEN = 'mock_token'

MOCK_TITLE = {
    "id": 1,
    "name": "Test Title",
    "description": "Test description",
    "trailer": "example_trailer",
    "reviews": 10,
    "image": "/static/titles/example.jpg",
    "slug": "test-title",
}

MOCK_ADMIN = Users(**{
        "id": 4,
        "username": "admin",
        "email": "admin@example.com",
        "role": RoleEnum.admin,
        "hashed_password": "password",
        "isActive": True,
        "avatar": "/static/avatars/default.jpg",
    })

MOCK_USER = Users(**{
        "id": 3,
        "username": "testuser",
        "email": "testuser@example.com",
        "role": RoleEnum.user,
        "hashed_password": "password",
        "isActive": True,
        "avatar": "/static/avatars/default.jpg",
    })

app.include_router(router)

client = TestClient(app)

@pytest.fixture
def mock_title_service():
    service = MagicMock(spec=TitleService)
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
def mock_user_service():
    service = MagicMock(spec=UserService)
    return service

@pytest.fixture
def override_dependencies(mock_title_service, mock_file_service, mock_user_service):
    app.dependency_overrides[TitleService] = lambda: mock_title_service
    app.dependency_overrides[FileService] = lambda: mock_file_service
    app.dependency_overrides[UserService] = lambda: mock_user_service
    app.dependency_overrides[OAuth2PasswordBearer] = lambda: mock_oauth2_bearer
    yield
    app.dependency_overrides = {}


def test_get_titles(mock_title_service, override_dependencies):
    page = 1
    limit = 10
    mock_titles = [
        Title(**MOCK_TITLE),
        Title(**{
            "id": 2,
            "name": "Test Title2",
            "description": "Test description2",
            "trailer": "example_trailer2",
            "reviews": 10,
            "image": "/static/titles/example2.jpg",
            "slug": "test-title2",
            }),
    ]
    mock_title_service.get_titles.return_value = {
        "titles": mock_titles,
        "total": 2,
        "page": page,
        "limit": limit,
    }

    response = client.get(
        "/titles", params={"page": page, "limit": limit}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["titles"] != None
    assert data["total"] == 2
    assert data["page"] == page
    assert data["limit"] == limit
    mock_title_service.get_titles.assert_called_once_with(page=page, limit=limit, name="")

def test_get_titles_filtered_by_name(mock_title_service, override_dependencies):
    page = 1
    limit = 10
    name = "Test"
    mock_titles = [Title(**MOCK_TITLE)]
    mock_title_service.get_titles.return_value = {
        "titles": mock_titles,
        "total": 1,
        "page": page,
        "limit": limit,
    }

    response = client.get(
        "/titles", params={"page": page, "limit": limit, "name": name}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["titles"] != None
    assert data["total"] == 1
    assert data["page"] == page
    assert data["limit"] == limit
    mock_title_service.get_titles.assert_called_once_with(page=page, limit=limit, name=name)

def test_get_titles_no_results(mock_title_service, override_dependencies):
    page = 1
    limit = 10
    mock_title_service.get_titles.return_value = {
        "titles": [],
        "total": 0,
        "page": page,
        "limit": limit,
    }

    response = client.get(
        "/titles", params={"page": page, "limit": limit}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["titles"] == []
    assert data["total"] == 0
    assert data["page"] == page
    assert data["limit"] == limit
    mock_title_service.get_titles.assert_called_once_with(page=page, limit=limit, name="")


def test_get_title_by_slug_success(mock_title_service, override_dependencies):
    mock_title_service.get_title_by_slug.return_value = Title(**MOCK_TITLE)
    slug = MOCK_TITLE["slug"]

    response = client.get(f"/titles/{slug}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == MOCK_TITLE["id"]
    assert data["name"] == MOCK_TITLE["name"]
    assert data["description"] == MOCK_TITLE["description"]
    assert data["trailer"] == MOCK_TITLE["trailer"]
    assert data["reviews"] == MOCK_TITLE["reviews"]
    assert data["image"] == MOCK_TITLE["image"]
    assert data["slug"] == MOCK_TITLE["slug"]
    mock_title_service.get_title_by_slug.assert_called_once_with(slug=slug)


def test_get_title_by_slug_not_found(mock_title_service, override_dependencies):
    mock_title_service.get_title_by_slug.return_value = None
    slug = "non-existent-title"

    response = client.get(f"/titles/{slug}")

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Title not found"
    mock_title_service.get_title_by_slug.assert_called_once_with(slug=slug)


def test_create_title_success(mock_title_service, mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MOCK_ADMIN
    new_title = {
        "name": "New Title",
        "description": "Description of the new title",
        "trailer": "trailer_url",
        "image": "image_url",
        "slug": "new-title"
    }
    created_title = {
        "id": 1,
        "name": "New Title",
        "description": "Description of the new title",
        "trailer": "trailer_url",
        "image": "image_url",
        "slug": "new-title"
    }

    mock_title_service.create_title.return_value = created_title

    response = client.post(
        "/titles",
        json=new_title,
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == created_title["id"]
    assert data["name"] == created_title["name"]
    assert data["description"] == created_title["description"]
    assert data["trailer"] == created_title["trailer"]
    assert data["image"] == created_title["image"]
    assert data["slug"] == created_title["slug"]
    mock_user_service.get_current_user.assert_called_once_with(MOCK_TOKEN)
    mock_title_service.create_title.assert_called_once_with(title=TitleCreate(**new_title))


def test_create_title_access_denied(mock_title_service, mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MOCK_USER
    new_title = {
        "name": "New Title",
        "description": "Description of the new title",
        "trailer": "trailer_url",
        "image": "image_url",
        "slug": "new-title"
    }

    response = client.post(
        "/titles",
        json=new_title,
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )

    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Access denied. Admin role required."
    mock_user_service.get_current_user.assert_called_once_with(MOCK_TOKEN)
    mock_title_service.create_title.assert_not_called()


def test_create_title_validation_error(mock_title_service, mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MOCK_ADMIN
    invalid_title = {
        "description": "Description of the new title",
        "trailer": "trailer_url",
        "image": "image_url",
        "slug": "new-title"
    }

    response = client.post(
        "/titles",
        json=invalid_title,
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )

    assert response.status_code == 422
    mock_user_service.get_current_user.assert_called_once_with(MOCK_TOKEN)
    mock_title_service.create_title.assert_not_called()


def test_partial_update_title_success(mock_title_service, mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MOCK_ADMIN
    updated_data = {
        "name": "Updated Title",
        "reviews": 5
        }
    title_id = 1
    updated_title = {
        "id": title_id,
        "name": "Updated Title",
        "description": "Original Description",
        "trailer": "original_trailer",
        "reviews": 5,
        "image": "original_image_url",
        "slug": "original-slug"
    }

    mock_title_service.partial_update_title.return_value = updated_title

    response = client.patch(
        f"/titles/{title_id}",
        json=updated_data,
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == updated_title["id"]
    assert data["name"] == updated_title["name"]
    assert data["description"] == updated_title["description"]
    assert data["trailer"] == updated_title["trailer"]
    assert data["reviews"] == updated_title["reviews"]
    assert data["image"] == updated_title["image"]
    assert data["slug"] == updated_title["slug"]
    mock_user_service.get_current_user.assert_called_once_with(MOCK_TOKEN)
    mock_title_service.partial_update_title.assert_called_once_with(id=title_id, title=TitleUpdate(**updated_data))


def test_partial_update_title_not_found(mock_title_service, mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MOCK_ADMIN
    updated_data = {
        "trailer": "Updated_trailer",
        "reviews": 5
        }
    title_id = 99

    mock_title_service.partial_update_title.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Title not found"
    )

    response = client.patch(
        f"/titles/{title_id}",
        json=updated_data,
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Title not found"
    mock_user_service.get_current_user.assert_called_once_with(MOCK_TOKEN)
    mock_title_service.partial_update_title.assert_called_once_with(id=title_id, title=TitleUpdate(**updated_data))


def test_partial_update_title_access_denied(mock_title_service, mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MOCK_USER
    updated_data = {"name": "Updated Title"}
    title_id = 1

    response = client.patch(
        f"/titles/{title_id}",
        json=updated_data,
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )

    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Access denied. Admin role required."
    mock_user_service.get_current_user.assert_called_once_with(MOCK_TOKEN)
    mock_title_service.partial_update_title.assert_not_called()


def test_partial_update_title_validation_error(mock_title_service, mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MOCK_ADMIN
    invalid_data = {"reviews": "invalid_type"}
    title_id = 1

    response = client.patch(
        f"/titles/{title_id}",
        json=invalid_data,
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )

    assert response.status_code == 422
    mock_user_service.get_current_user.assert_called_once_with(MOCK_TOKEN)
    mock_title_service.partial_update_title.assert_not_called()


def test_delete_title_success(mock_title_service, mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MOCK_ADMIN
    title_id = 1
    mock_title_service.delete_title.return_value = {"detail": "Title deleted successfully"}

    response = client.delete(
        f"/titles/{title_id}",
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )

    assert response.status_code == 200
    assert response.json() == {"detail": "Title deleted successfully"}

    mock_user_service.get_current_user.assert_called_once_with(MOCK_TOKEN)
    mock_title_service.delete_title.assert_called_once_with(id=title_id)

def test_delete_title_not_found(mock_title_service, mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MOCK_ADMIN
    title_id = 99
    mock_title_service.delete_title.side_effect = HTTPException(
        status_code=404, detail="Title not found"
    )

    response = client.delete(
        f"/titles/{title_id}",
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Title not found"}

    mock_user_service.get_current_user.assert_called_once_with(MOCK_TOKEN)
    mock_title_service.delete_title.assert_called_once_with(id=title_id)

def test_delete_title_forbidden(mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MOCK_USER
    title_id = 1

    response = client.delete(
        f"/titles/{title_id}",
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Access denied. Admin role required."}

    mock_user_service.get_current_user.assert_called_once_with(MOCK_TOKEN)


def test_upload_image_success(mock_file_service, mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MOCK_ADMIN
    mock_file_service.process_image.return_value = "/static/titles/new_image.jpg"

    file_data = BytesIO(b"fake image content")
    response = client.post(
        "/titles/change/image",
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"},
        files={"file": ("test_image.jpg", file_data, "image/jpeg")},
        data={"old_image": "/static/titles/old_image.jpg"}
    )

    assert response.status_code == 200
    assert response.json() == "/static/titles/new_image.jpg"
    mock_user_service.get_current_user.assert_called_once_with(MOCK_TOKEN)
    mock_file_service.process_image.assert_called_once()

def test_upload_image_invalid_file_type(mock_file_service, mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MOCK_ADMIN
    mock_file_service.process_image.side_effect = HTTPException(
        status_code=400, detail="Invalid file type. Only JPEG and PNG are allowed."
    )

    file_data = BytesIO(b"fake image content")
    response = client.post(
        "/titles/change/image",
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"},
        files={"file": ("test_image.txt", file_data, "text/plain")},
        data={"old_image": "/static/titles/old_image.jpg"}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid file type. Only JPEG and PNG are allowed."}
    mock_user_service.get_current_user.assert_called_once_with(MOCK_TOKEN)
    mock_file_service.process_image.assert_called_once()

def test_upload_image_unauthorized(mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MOCK_USER

    file_data = BytesIO(b"fake image content")
    response = client.post(
        "/titles/change/image",
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"},
        files={"file": ("test_image.jpg", file_data, "image/jpeg")},
        data={"old_image": "/static/titles/old_image.jpg"}
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Access denied. Admin role required."}
    mock_user_service.get_current_user.assert_called_once_with(MOCK_TOKEN)

def test_upload_image_file_service_error(mock_file_service, mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MOCK_ADMIN
    mock_file_service.process_image.side_effect = HTTPException(
        status_code=500, detail="Internal server error."
    )

    file_data = BytesIO(b"fake image content")
    response = client.post(
        "/titles/change/image",
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"},
        files={"file": ("test_image.jpg", file_data, "image/jpeg")},
        data={"old_image": "/static/titles/old_image.jpg"}
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error."}
    mock_user_service.get_current_user.assert_called_once_with(MOCK_TOKEN)
    mock_file_service.process_image.assert_called_once()
