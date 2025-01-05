import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from models.reaction import Reaction, ReactionTypeEnum
from schemas.reaction_schema import *
from service.reaction_service import ReactionService
from service.user_service import UserService
from controllers.reaction import router
from fastapi.security import OAuth2PasswordBearer
from models.user import Users, RoleEnum


MOCK_TOKEN = 'mock_token'

MOCK_REACTION = Reaction(**{
        "id": 1,
        "user_id": 1,
        "title_id": 1,
        "review_id": None,
        "type": ReactionTypeEnum.like
    })

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
def mock_reaction_service():
    service = MagicMock(spec=ReactionService)
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
def override_dependencies(mock_reaction_service, mock_user_service):
    app.dependency_overrides[ReactionService] = lambda: mock_reaction_service
    app.dependency_overrides[UserService] = lambda: mock_user_service
    app.dependency_overrides[OAuth2PasswordBearer] = lambda: mock_oauth2_bearer
    yield
    app.dependency_overrides = {}


def test_process_reaction_create(mock_reaction_service, mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MOCK_USER
    mock_reaction_service.process_reaction.return_value = None

    reaction_data = {"title_id": 1, "review_id": None, "type": "like"}

    response = client.post(
        "/reaction", json=reaction_data, headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )

    assert response.status_code == 204
    mock_reaction_service.process_reaction.assert_called_once_with(MOCK_USER.id, ReactionRequest(**reaction_data))


def test_process_reaction_forbidden(mock_reaction_service, mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = None

    reaction_data = {"title_id": 1, "review_id": None, "type": "like"}

    response = client.post(
        "/reaction", json=reaction_data, headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied. Authentication required."


def test_process_reaction_not_found(mock_reaction_service, mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MOCK_USER
    mock_reaction_service.process_reaction.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Reaction not found"
    )

    reaction_data = {"title_id": None, "review_id": None, "type": "like"}

    response = client.post(
        "/reaction", json=reaction_data, headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Reaction not found"


def test_process_reaction_validation_error(mock_reaction_service, mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MOCK_USER

    invalid_reaction_data = {"title_id": None, "review_id": None, "type": "invalid"}

    response = client.post(
        "/reaction", json=invalid_reaction_data, headers={"Authorization": f"Bearer {MOCK_TOKEN}"}
    )

    assert response.status_code == 422


def test_get_reactions_with_titles(mock_reaction_service, mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MOCK_USER
    mock_reaction_service.count_title_reactions.return_value = {
        "reactions": [
            {
                "title_id": 1,
                "review_id": None,
                "current_user_reaction": "like",
                "likes": 10,
                "dislikes": 2,
            }
        ]
    }

    response = client.get("/reaction/count", params={"title_ids": [1, 2]}, headers={"Authorization": f"Bearer {MOCK_TOKEN}"})

    assert response.status_code == 200
    assert response.json() == {
        "reactions": [
            {
                "title_id": 1,
                "review_id": None,
                "current_user_reaction": "like",
                "likes": 10,
                "dislikes": 2,
            }
        ]
    }
    mock_reaction_service.count_title_reactions.assert_called_once_with([1, 2], MOCK_USER)


def test_get_reactions_with_reviews(mock_reaction_service, mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = MOCK_USER
    mock_reaction_service.count_review_reactions.return_value = {
        "reactions": [
            {
                "title_id": None,
                "review_id": 1,
                "current_user_reaction": None,
                "likes": 5,
                "dislikes": 1,
            }
        ]
    }

    response = client.get("/reaction/count", params={"review_ids": [1, 2]}, headers={"Authorization": f"Bearer {MOCK_TOKEN}"})

    assert response.status_code == 200
    assert response.json() == {
        "reactions": [
            {
                "title_id": None,
                "review_id": 1,
                "current_user_reaction": None,
                "likes": 5,
                "dislikes": 1,
            }
        ]
    }
    mock_reaction_service.count_review_reactions.assert_called_once_with([1, 2], MOCK_USER)


def test_get_reactions_no_user(mock_reaction_service, mock_user_service, override_dependencies):
    mock_user_service.get_current_user.return_value = None
    mock_reaction_service.count_title_reactions.return_value = {
        "reactions": [
            {
                "title_id": 1,
                "review_id": None,
                "current_user_reaction": None,
                "likes": 10,
                "dislikes": 2,
            }
        ]
    }

    response = client.get("/reaction/count", params={"title_ids": [1, 2]})

    assert response.status_code == 200
    assert response.json() == {
        "reactions": [
            {
                "title_id": 1,
                "review_id": None,
                "current_user_reaction": None,
                "likes": 10,
                "dislikes": 2,
            }
        ]
    }
    mock_reaction_service.count_title_reactions.assert_called_once_with([1, 2], None)
