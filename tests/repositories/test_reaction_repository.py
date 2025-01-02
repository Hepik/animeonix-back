import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session, Query
from models.reaction import Reaction, ReactionTypeEnum
from repository.reaction_repository import ReactionRepository
from schemas.reaction_schema import *

MOCK_REACTION = Reaction(**{
    "id": 1,
    "user_id": 2,
    "title_id": 3,
    "review_id": None,
    "type": ReactionTypeEnum.like
})

@pytest.fixture
def mock_db_query():
    query = MagicMock(spec=Query)
    return query

@pytest.fixture
def mock_db_session():
    session = MagicMock(spec=Session)
    return session

def test_get_reaction_by_title_id(mock_db_session, mock_db_query):
    user_id = 2
    title_id = 3
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter_by.return_value = mock_db_query
    mock_db_query.first.return_value = MOCK_REACTION

    repository = ReactionRepository(mock_db_session)
    result = repository.get_reaction_by_title_id(user_id, title_id)

    assert result == MOCK_REACTION
    mock_db_query.filter_by.assert_called_once_with(title_id=title_id, user_id=user_id)

def test_get_reaction_by_review_id(mock_db_session, mock_db_query):
    user_id = 2
    review_id = 4
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter_by.return_value = mock_db_query
    mock_db_query.first.return_value = MOCK_REACTION

    repository = ReactionRepository(mock_db_session)
    result = repository.get_reaction_by_review_id(user_id, review_id)

    assert result == MOCK_REACTION
    mock_db_query.filter_by.assert_called_once_with(review_id=review_id, user_id=user_id)

def test_delete_reaction(mock_db_session):
    mock_db_session.delete.return_value = None
    mock_db_session.commit.return_value = None

    repository = ReactionRepository(mock_db_session)
    result = repository.delete_reaction(MOCK_REACTION)

    assert result is True
    mock_db_session.delete.assert_called_once_with(MOCK_REACTION)
    mock_db_session.commit.assert_called_once()

def test_update_reaction(mock_db_session):
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = MOCK_REACTION

    repository = ReactionRepository(mock_db_session)
    result = repository.update_reaction(MOCK_REACTION)

    assert result is True
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(MOCK_REACTION)

def test_create_reaction(mock_db_session):
    user_id = 2
    reaction_data = ReactionRequest(**{
        "title_id": 3,
        "review_id": None,
        "type": ReactionTypeEnum.like
        })
    new_reaction = Reaction(**{
        "id": 1,
        "user_id": user_id,
        "title_id": reaction_data.title_id,
        "review_id": reaction_data.review_id,
        "type": reaction_data.type
    })
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = new_reaction

    repository = ReactionRepository(mock_db_session)
    result = repository.create_reaction(user_id, reaction_data)

    assert result.type == reaction_data.type
    assert result.title_id == reaction_data.title_id
    assert result.review_id == reaction_data.review_id
    mock_db_session.add.assert_called_once_with(result)
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(result)

def test_get_reaction_by_title_ids(mock_db_session, mock_db_query):
    title_ids = [1, 2, 3]
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.where.return_value = [MOCK_REACTION]

    repository = ReactionRepository(mock_db_session)
    result = repository.get_reaction_by_title_ids(title_ids)

    assert result == [MOCK_REACTION]
    mock_db_query.where.assert_called_once()

def test_get_reaction_by_review_ids(mock_db_session, mock_db_query):
    review_ids = [4, 5, 6]
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.where.return_value = [MOCK_REACTION]

    repository = ReactionRepository(mock_db_session)
    result = repository.get_reaction_by_review_ids(review_ids)
    
    assert result == [MOCK_REACTION]
    mock_db_query.where.assert_called_once()
