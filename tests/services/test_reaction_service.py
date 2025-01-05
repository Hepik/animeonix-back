import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException, status
from service.reaction_service import ReactionService
from schemas.reaction_schema import ReactionRequest, ReactionTypeEnum
from models.reaction import Reaction
from models.user import Users, RoleEnum


MOCK_USER = Users(**{
        "id": 4,
        "username": "testuser",
        "email": "testuser@example.com",
        "role": RoleEnum.user,
        "hashed_password": "password",
        "isActive": True,
        "avatar": "/static/avatars/default.jpg",
    })

MOCK_REACTION = Reaction(**{
    "id": 1,
    "user_id": 1,
    "title_id": 1,
    "review_id": None,
    "type": ReactionTypeEnum.like
})

MOCK_REACTIONS = [
    Reaction(**{
        "id": 1,
        "user_id": 4,
        "title_id": 1,
        "review_id": None,
        "type": ReactionTypeEnum.like
    }),
    Reaction(**{
        "id": 2,
        "user_id": 2,
        "title_id": 1,
        "review_id": None,
        "type": ReactionTypeEnum.dislike
    }),
    Reaction(**{
        "id": 3,
        "user_id": 4,
        "title_id": 2,
        "review_id": None,
        "type": ReactionTypeEnum.like
    }),
]

MOCK_REACTIONS_REVIEW = [
    Reaction(**{
        "id": 1,
        "user_id": 4,
        "title_id": None,
        "review_id": 1,
        "type": ReactionTypeEnum.like
    }),
    Reaction(**{
        "id": 2,
        "user_id": 2,
        "title_id": None,
        "review_id": 1,
        "type": ReactionTypeEnum.dislike
    }),
    Reaction(**{
        "id": 3,
        "user_id": 4,
        "title_id": None,
        "review_id": 2,
        "type": ReactionTypeEnum.like
    }),
]

@pytest.fixture
def mock_reaction_repository():
    repo = MagicMock()
    return repo

@pytest.fixture
def reaction_service(mock_reaction_repository):
    return ReactionService(mock_reaction_repository)


def test_process_reaction_create(reaction_service, mock_reaction_repository):
    reaction_request = ReactionRequest(title_id=1, type=ReactionTypeEnum.like)
    mock_reaction_repository.get_reaction_by_title_id.return_value = None
    mock_reaction_repository.create_reaction.return_value = MOCK_REACTION

    result = reaction_service.process_reaction(user_id=1, reaction=reaction_request)

    assert result == MOCK_REACTION
    mock_reaction_repository.get_reaction_by_title_id.assert_called_once_with(1, 1)
    mock_reaction_repository.create_reaction.assert_called_once_with(1, reaction_request)


def test_process_reaction_update(reaction_service, mock_reaction_repository):
    existing_reaction = Reaction(**{
        "id": 1,
        "user_id": 1,
        "title_id": 1,
        "review_id": None,
        "type": ReactionTypeEnum.dislike
    })
    reaction_request = ReactionRequest(title_id=1, type=ReactionTypeEnum.like)
    mock_reaction_repository.get_reaction_by_title_id.return_value = existing_reaction

    result = reaction_service.process_reaction(user_id=1, reaction=reaction_request)

    assert existing_reaction.type == ReactionTypeEnum.like
    mock_reaction_repository.get_reaction_by_title_id.assert_called_once_with(1, 1)
    mock_reaction_repository.update_reaction.assert_called_once_with(existing_reaction)


def test_process_reaction_delete(reaction_service, mock_reaction_repository):
    existing_reaction = Reaction(**{
        "id": 1,
        "user_id": 1,
        "title_id": 1,
        "review_id": None,
        "type": ReactionTypeEnum.like
    })
    reaction_request = ReactionRequest(title_id=1, type=ReactionTypeEnum.like)
    mock_reaction_repository.get_reaction_by_title_id.return_value = existing_reaction

    result = reaction_service.process_reaction(user_id=1, reaction=reaction_request)

    assert result is None
    mock_reaction_repository.get_reaction_by_title_id.assert_called_once_with(1, 1)
    mock_reaction_repository.delete_reaction.assert_called_once_with(existing_reaction)


def test_process_reaction_review_create(reaction_service, mock_reaction_repository):
    reaction_request = ReactionRequest(review_id=1, type=ReactionTypeEnum.like)
    mock_reaction_repository.get_reaction_by_review_id.return_value = None
    mock_reaction_repository.create_reaction.return_value = MOCK_REACTION

    result = reaction_service.process_reaction(user_id=1, reaction=reaction_request)

    assert result == MOCK_REACTION
    mock_reaction_repository.get_reaction_by_review_id.assert_called_once_with(1, 1)
    mock_reaction_repository.create_reaction.assert_called_once_with(1, reaction_request)


def test_process_reaction_review_update(reaction_service, mock_reaction_repository):
    existing_reaction = Reaction(**{
        "id": 1,
        "user_id": 1,
        "title_id": None,
        "review_id": 1,
        "type": ReactionTypeEnum.dislike
    })
    reaction_request = ReactionRequest(review_id=1, type=ReactionTypeEnum.like)
    mock_reaction_repository.get_reaction_by_review_id.return_value = existing_reaction

    result = reaction_service.process_reaction(user_id=1, reaction=reaction_request)

    assert existing_reaction.type == ReactionTypeEnum.like
    mock_reaction_repository.get_reaction_by_review_id.assert_called_once_with(1, 1)
    mock_reaction_repository.update_reaction.assert_called_once_with(existing_reaction)


def test_process_reaction_review_delete(reaction_service, mock_reaction_repository):
    existing_reaction = Reaction(**{
        "id": 1,
        "user_id": 1,
        "title_id": None,
        "review_id": 1,
        "type": ReactionTypeEnum.like
    })
    reaction_request = ReactionRequest(review_id=1, type=ReactionTypeEnum.like)
    mock_reaction_repository.get_reaction_by_review_id.return_value = existing_reaction

    result = reaction_service.process_reaction(user_id=1, reaction=reaction_request)

    assert result is None
    mock_reaction_repository.get_reaction_by_review_id.assert_called_once_with(1, 1)
    mock_reaction_repository.delete_reaction.assert_called_once_with(existing_reaction)


def test_process_reaction_invalid_input(reaction_service, mock_reaction_repository):
    reaction_request = ReactionRequest(type=ReactionTypeEnum.like)

    with pytest.raises(HTTPException) as exc_info:
        reaction_service.process_reaction(user_id=1, reaction=reaction_request)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Reaction not found"


def test_count_title_reactions_no_current_user(reaction_service, mock_reaction_repository):
    mock_reaction_repository.get_reaction_by_title_ids.return_value = MOCK_REACTIONS
    title_ids = [1, 2]

    result = reaction_service.count_title_reactions(title_ids)

    assert result == {
        "reactions": [
            {
                "title_id": 1,
                "current_user_reaction": None,
                "likes": 1,
                "dislikes": 1
            },
            {
                "title_id": 2,
                "current_user_reaction": None,
                "likes": 1,
                "dislikes": 0
            }
        ]
    }
    mock_reaction_repository.get_reaction_by_title_ids.assert_called_once_with(title_ids)


def test_count_title_reactions_with_current_user(reaction_service, mock_reaction_repository):
    mock_reaction_repository.get_reaction_by_title_ids.return_value = MOCK_REACTIONS
    title_ids = [1, 2]

    result = reaction_service.count_title_reactions(title_ids, current_user=MOCK_USER)

    assert result == {
        "reactions": [
            {
                "title_id": 1,
                "current_user_reaction": ReactionTypeEnum.like,
                "likes": 1,
                "dislikes": 1
            },
            {
                "title_id": 2,
                "current_user_reaction": ReactionTypeEnum.like,
                "likes": 1,
                "dislikes": 0
            }
        ]
    }
    mock_reaction_repository.get_reaction_by_title_ids.assert_called_once_with(title_ids)


def test_count_title_reactions_empty_list(reaction_service, mock_reaction_repository):
    mock_reaction_repository.get_reaction_by_title_ids.return_value = []
    title_ids = []

    result = reaction_service.count_title_reactions(title_ids)

    assert result == {"reactions": []}
    mock_reaction_repository.get_reaction_by_title_ids.assert_called_once_with(title_ids)


def test_count_title_reactions_mixed_data(reaction_service, mock_reaction_repository):
    reactions = [
        Reaction(**{
            "id": 1,
            "user_id": 1,
            "title_id": 3,
            "review_id": None,
            "type": ReactionTypeEnum.dislike
        }),
        Reaction(**{
            "id": 2,
            "user_id": 2,
            "title_id": 3,
            "review_id": None,
            "type": ReactionTypeEnum.like
        })
    ]
    mock_reaction_repository.get_reaction_by_title_ids.return_value = reactions
    title_ids = [3]

    result = reaction_service.count_title_reactions(title_ids, current_user=MOCK_USER)

    assert result == {
        "reactions": [
            {
                "title_id": 3,
                "current_user_reaction": None,
                "likes": 1,
                "dislikes": 1
            }
        ]
    }
    mock_reaction_repository.get_reaction_by_title_ids.assert_called_once_with(title_ids)


def test_count_review_reactions_no_current_user(reaction_service, mock_reaction_repository):
    mock_reaction_repository.get_reaction_by_review_ids.return_value = MOCK_REACTIONS_REVIEW
    review_ids = [1, 2]

    result = reaction_service.count_review_reactions(review_ids)

    assert result == {
        "reactions": [
            {
                "review_id": 1,
                "current_user_reaction": None,
                "likes": 1,
                "dislikes": 1,
                "user_id": 4
            },
            {
                "review_id": 2,
                "current_user_reaction": None,
                "likes": 1,
                "dislikes": 0,
                "user_id": 4
            }
        ]
    }
    mock_reaction_repository.get_reaction_by_review_ids.assert_called_once_with(review_ids)


def test_count_review_reactions_with_current_user(reaction_service, mock_reaction_repository):
    mock_reaction_repository.get_reaction_by_review_ids.return_value = MOCK_REACTIONS_REVIEW
    review_ids = [1, 2]

    result = reaction_service.count_review_reactions(review_ids, current_user=MOCK_USER)

    assert result == {
        "reactions": [
            {
                "review_id": 1,
                "current_user_reaction": ReactionTypeEnum.like,
                "likes": 1,
                "dislikes": 1,
                "user_id": 4
            },
            {
                "review_id": 2,
                "current_user_reaction": ReactionTypeEnum.like,
                "likes": 1,
                "dislikes": 0,
                "user_id": 4
            }
        ]
    }
    mock_reaction_repository.get_reaction_by_review_ids.assert_called_once_with(review_ids)


def test_count_review_reactions_empty_list(reaction_service, mock_reaction_repository):
    mock_reaction_repository.get_reaction_by_review_ids.return_value = []
    review_ids = []

    result = reaction_service.count_review_reactions(review_ids)

    assert result == {"reactions": []}
    mock_reaction_repository.get_reaction_by_review_ids.assert_called_once_with(review_ids)


def test_count_review_reactions_mixed_data(reaction_service, mock_reaction_repository):
    reactions = [
        Reaction(**{
            "id": 1,
            "user_id": 1,
            "review_id": 3,
            "title_id": None,
            "type": ReactionTypeEnum.dislike
        }),
        Reaction(**{
            "id": 2,
            "user_id": 2,
            "review_id": 3,
            "title_id": None,
            "type": ReactionTypeEnum.like
        })
    ]
    mock_reaction_repository.get_reaction_by_review_ids.return_value = reactions
    review_ids = [3]

    result = reaction_service.count_review_reactions(review_ids, current_user=MOCK_USER)

    assert result == {
        "reactions": [
            {
                "review_id": 3,
                "current_user_reaction": None,
                "likes": 1,
                "dislikes": 1,
                "user_id": 1
            }
        ]
    }
    mock_reaction_repository.get_reaction_by_review_ids.assert_called_once_with(review_ids)

