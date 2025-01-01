import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from schemas.review_schema import *
from service.review_service import ReviewService
from service.user_service import UserService
from controllers.review import router
from fastapi.security import OAuth2PasswordBearer
from models.user import Users, RoleEnum


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

MOCK_USER = Users(**{
        "id": 3,
        "username": "testuser",
        "email": "testuser@example.com",
        "role": RoleEnum.user,
        "hashed_password": "password",
        "isActive": True,
        "avatar": "/static/avatars/default.jpg",
    })

MOCK_REVIEW = {
    "id": 1,
    "content": "Amazing title!",
    "title_id": 1,
    "user_id": 1
}

MOCK_REVIEWS = [
    {
        "id": 1,
        "content": "Great title!",
        "title_id": 1,
        "user_id": 1
    },
    {
        "id": 2,
        "content": "Not bad.",
        "title_id": 1,
        "user_id": 2
    },
]

app.include_router(router)

client = TestClient(app)

@pytest.fixture
def mock_review_service():
    service = MagicMock(spec=ReviewService)
    return service

@pytest.fixture
def mock_oauth2_bearer():
    def fake_oauth2_bearer():
        return MOCK_TOKEN
    return fake_oauth2_bearer

@pytest.fixture
def mock_user_service():
    service = MagicMock(spec=UserService)
    return service

@pytest.fixture
def override_dependencies(mock_review_service, mock_user_service):
    app.dependency_overrides[ReviewService] = lambda: mock_review_service
    app.dependency_overrides[UserService] = lambda: mock_user_service
    app.dependency_overrides[OAuth2PasswordBearer] = lambda: mock_oauth2_bearer
    yield
    app.dependency_overrides = {}


def test_get_reviews(mock_review_service, override_dependencies):
    page = 1
    limit = 10
    mock_review_service.get_reviews.return_value = {
        "reviews": MOCK_REVIEWS,
        "total": 2,
        "page": page,
        "limit": limit
    }

    response = client.get("/reviews", params={"page": page, "limit": limit})
    
    assert response.status_code == 200
    data = response.json()
    assert data["reviews"] == MOCK_REVIEWS
    assert data["total"] == 2
    assert data["page"] == page
    assert data["limit"] == limit
    mock_review_service.get_reviews.assert_called_once_with(page=page, limit=limit, title_id=None)


def test_get_reviews_filtered_by_title(mock_review_service, override_dependencies):
    page = 1
    limit = 10
    title_id = 1
    mock_review_service.get_reviews.return_value = {
        "reviews": MOCK_REVIEWS,
        "total": 2,
        "page": page,
        "limit": limit
    }

    response = client.get("/reviews", params={"page": page, "limit": limit, "title_id": title_id})

    assert response.status_code == 200
    data = response.json()
    assert data["reviews"] == MOCK_REVIEWS
    assert data["total"] == 2
    assert data["page"] == page
    assert data["limit"] == limit
    mock_review_service.get_reviews.assert_called_once_with(page=page, limit=limit, title_id=title_id)


def test_get_reviews_no_results(mock_review_service, override_dependencies):
    page = 1
    limit = 10
    mock_review_service.get_reviews.return_value = {
        "reviews": [],
        "total": 0,
        "page": page,
        "limit": limit
    }

    response = client.get("/reviews", params={"page": page, "limit": limit})

    assert response.status_code == 200
    data = response.json()
    assert data["reviews"] == []
    assert data["total"] == 0
    assert data["page"] == page
    assert data["limit"] == limit
    mock_review_service.get_reviews.assert_called_once_with(page=page, limit=limit, title_id=None)


def test_get_review_by_id_success(mock_review_service, override_dependencies):
    review_id = MOCK_REVIEW["id"]
    mock_review_service.get_review_by_id.return_value = MOCK_REVIEW

    response = client.get(f"/reviews/{review_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == MOCK_REVIEW["id"]
    assert data["content"] == MOCK_REVIEW["content"]
    assert data["title_id"] == MOCK_REVIEW["title_id"]
    assert data["user_id"] == MOCK_REVIEW["user_id"]
    mock_review_service.get_review_by_id.assert_called_once_with(id=review_id)


def test_get_review_by_id_invalid_id(mock_review_service, override_dependencies):
    invalid_review_id = "invalid"

    response = client.get(f"/reviews/{invalid_review_id}")
    assert response.status_code == 422


def test_create_review_success(mock_review_service, mock_user_service, override_dependencies):
    review_data = {
        "content": "Amazing title!",
        "title_id": 1
    }
    mock_user_service.get_current_user.return_value = MOCK_USER
    mock_review_service.create_review.return_value = MOCK_REVIEW

    response = client.post("/reviews", json=review_data, headers={"Authorization": f"Bearer {MOCK_TOKEN}"})

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == MOCK_REVIEW["id"]
    assert data["content"] == MOCK_REVIEW["content"]
    assert data["title_id"] == MOCK_REVIEW["title_id"]
    assert data["user_id"] == MOCK_REVIEW["user_id"]

    expected_review = ReviewCreate(**review_data)
    mock_review_service.create_review.assert_called_once_with(
        review=expected_review,
        user_id=MOCK_USER.id
    )


def test_create_review_unauthorized(mock_review_service, mock_user_service):
    mock_user_service.get_current_user.side_effect = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token is not valid."
    )

    review_data = {
        "content": "Great movie!",
        "title_id": 1
    }

    response = client.post("/reviews", json=review_data)

    assert response.status_code == 401


def test_create_review_invalid_data(mock_review_service, override_dependencies):
    invalid_review_data = {
        "content": "",
        "title_id": "invalid_id"
    }

    response = client.post("/reviews", json=invalid_review_data, headers={"Authorization": f"Bearer {MOCK_TOKEN}"})

    assert response.status_code == 422


def test_delete_review_success(mock_review_service, mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MOCK_USER
    mock_review_service.get_review_by_id.return_value = MOCK_REVIEW
    mock_review_service.delete_review.return_value = True

    response = client.delete(
        f"/reviews/{MOCK_REVIEW['id']}",
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "Review deleted successfully"
    mock_review_service.delete_review.assert_called_once_with(
        id=MOCK_REVIEW["id"],
        current_user=MOCK_USER
    )


def test_delete_review_not_found(mock_review_service, mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MOCK_USER
    mock_review_service.delete_review.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Review not found"
    )
    response = client.delete(
        f"/reviews/{MOCK_REVIEW['id']}",
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Review not found"
    mock_review_service.delete_review.assert_called_once_with(id=MOCK_REVIEW['id'], current_user=MOCK_USER)


def test_delete_review_forbidden(mock_review_service, mock_user_service, override_dependencies):
    MOCK_USER_NOT_OWNER = {"id": 2, "role": {"value": "user"}}
    mock_user_service.get_current_user.return_value = MOCK_USER_NOT_OWNER
    mock_review_service.delete_review.side_effect = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied. Admin role required."
    )

    response = client.delete(
        f"/reviews/{MOCK_REVIEW['id']}",
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )

    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Access denied. Admin role required."
    mock_review_service.delete_review.assert_called_once_with(id=MOCK_REVIEW['id'], current_user=MOCK_USER_NOT_OWNER)

def test_delete_review_admin(mock_review_service, mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MOCK_ADMIN
    mock_review_service.get_review_by_id.return_value = MOCK_REVIEW
    mock_review_service.delete_review.return_value = True

    response = client.delete(
        f"/reviews/{MOCK_REVIEW['id']}",
        headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "Review deleted successfully"
    mock_review_service.delete_review.assert_called_once_with(
        id=MOCK_REVIEW["id"],
        current_user=MOCK_ADMIN
    )
