from fastapi import HTTPException, status
import pytest
from unittest.mock import MagicMock
from models.review import Review
from schemas.review_schema import *
from service.review_service import ReviewService
from repository.review_repository import ReviewRepository
from models.user import Users, RoleEnum


MOCK_REVIEWS = [
    Review(**{
        "id": 1,
        "title_id": 1,
        "content": "Great review for title 1",
        "user_id": 5,
    }),
    Review(**{
        "id": 2,
        "title_id": 2,
        "content": "Average review for title 2",
        "user_id": 3,
    }),
]

MOCK_REVIEW = Review(**{
        "id": 3,
        "title_id": 1,
        "content": "review for title 1",
        "user_id": 4,
    })


MOCK_NEW_REVIEW = ReviewCreate(**{
    "content": "review for title 1",
    "title_id": 1,
})

MOCK_ADMIN = Users(**{
        "id": 5,
        "username": "admin",
        "email": "admin@example.com",
        "role": RoleEnum.admin,
        "hashed_password": "password",
        "isActive": True,
        "avatar": "/static/avatars/default.jpg",
    })

MOCK_USER = Users(**{
        "id": 4,
        "username": "testuser",
        "email": "testuser@example.com",
        "role": RoleEnum.user,
        "hashed_password": "password",
        "isActive": True,
        "avatar": "/static/avatars/default.jpg",
    })

MOCK_TOTAL_COUNT = 2
MOCK_REVIEW_COUNT = 1

@pytest.fixture
def mock_review_repository():
    repo = MagicMock(spec=ReviewRepository)
    return repo

@pytest.fixture
def review_service(mock_review_repository):
    return ReviewService(mock_review_repository)


def test_get_reviews_without_title_id(review_service, mock_review_repository):
    mock_review_repository.get_reviews.return_value = MOCK_REVIEWS
    mock_review_repository.get_reviews_count.return_value = MOCK_TOTAL_COUNT

    result = review_service.get_reviews(title_id=None, page=1, limit=10)

    assert result["reviews"] == MOCK_REVIEWS
    assert result["total"] == MOCK_TOTAL_COUNT
    assert result["page"] == 1
    assert result["limit"] == 10
    mock_review_repository.get_reviews.assert_called_once_with(skip=0, limit=10)
    mock_review_repository.get_reviews_count.assert_called_once()


def test_get_reviews_with_title_id(review_service, mock_review_repository):
    mock_review_repository.get_reviews_by_title.return_value = MOCK_REVIEW
    mock_review_repository.get_reviews_by_title_count.return_value = MOCK_REVIEW_COUNT

    result = review_service.get_reviews(title_id=1, page=1, limit=10)

    assert result["reviews"] == MOCK_REVIEW
    assert result["total"] == MOCK_REVIEW_COUNT
    assert result["page"] == 1
    assert result["limit"] == 10
    mock_review_repository.get_reviews_by_title.assert_called_once_with(title_id=1, skip=0, limit=10)
    mock_review_repository.get_reviews_by_title_count.assert_called_once_with(title_id=1)


def test_get_reviews_no_results(review_service, mock_review_repository):
    mock_review_repository.get_reviews_by_title.return_value = []
    mock_review_repository.get_reviews_by_title_count.return_value = 0

    result = review_service.get_reviews(title_id=999, page=1, limit=10)

    assert result["reviews"] == []
    assert result["total"] == 0
    assert result["page"] == 1
    assert result["limit"] == 10
    mock_review_repository.get_reviews_by_title.assert_called_once_with(title_id=999, skip=0, limit=10)
    mock_review_repository.get_reviews_by_title_count.assert_called_once_with(title_id=999)


def test_get_review_by_id_found(review_service, mock_review_repository):
    mock_review_repository.get_review_by_id.return_value = MOCK_REVIEW

    result = review_service.get_review_by_id(id=1)

    assert result == MOCK_REVIEW
    mock_review_repository.get_review_by_id.assert_called_once_with(id=1)


def test_get_review_by_id_not_found(review_service, mock_review_repository):
    mock_review_repository.get_review_by_id.return_value = None

    result = review_service.get_review_by_id(id=999)

    assert result is None
    mock_review_repository.get_review_by_id.assert_called_once_with(id=999)


def test_create_review(review_service, mock_review_repository):
    new_review_data = {
        "title_id": 1,
        "content": "review for title 1",
        "user_id": 4,
    }
    
    created_review_data = {
        "id": 1,
        **new_review_data
    }
    
    mock_review_repository.create_review.return_value = Review(**created_review_data)
    
    created_review = review_service.create_review(new_review_data, user_id=4)
    
    assert created_review.id == 1
    assert created_review.content == "review for title 1"
    assert created_review.user_id == 4
    assert created_review.title_id == 1
    mock_review_repository.create_review.assert_called_once_with(review=new_review_data, user_id=4)


def test_delete_review_success(review_service, mock_review_repository):
    mock_user = Users(**{
        "id": 4,
        "username": "test_user",
        "email": "test_user@example.com",
        "role": RoleEnum.user,
        "hashed_password": "password",
        "isActive": True,
        "avatar": "/static/avatars/default.jpg",
    })

    mock_review = Review(**{
        "id": 3,
        "title_id": 1,
        "content": "review for title 1",
        "user_id": 4,
    })
    
    mock_review_repository.get_review_by_id.return_value = mock_review
    mock_review_repository.delete_review.return_value = True

    result = review_service.delete_review(id=1, current_user=mock_user)

    assert result == {"detail": "Review deleted successfully"}
    mock_review_repository.delete_review.assert_called_once_with(id=1)


def test_delete_review_success_by_admin(review_service, mock_review_repository):
    mock_review_repository.get_review_by_id.return_value = MOCK_REVIEW
    mock_review_repository.delete_review.return_value = True

    result = review_service.delete_review(id=1, current_user=MOCK_ADMIN)

    assert result == {"detail": "Review deleted successfully"}
    mock_review_repository.delete_review.assert_called_once_with(id=1)


def test_delete_review_forbidden(review_service, mock_review_repository):
    mock_user = Users(**{
        "id": 1,
        "username": "testuser",
        "email": "testuser@example.com",
        "role": RoleEnum.user,
        "hashed_password": "password",
        "isActive": True,
        "avatar": "/static/avatars/default.jpg",
    })
    mock_review_repository.get_review_by_id.return_value = MOCK_REVIEW

    with pytest.raises(HTTPException) as exc_info:
        review_service.delete_review(id=1, current_user=mock_user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Access denied. Admin role required."
    mock_review_repository.delete_review.assert_not_called()


def test_delete_review_not_found(review_service, mock_review_repository):
    mock_review_repository.get_review_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        review_service.delete_review(id=999, current_user=MOCK_ADMIN)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Review not found"
    mock_review_repository.delete_review.assert_not_called()
