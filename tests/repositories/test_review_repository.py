import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session, Query
from models.review import Review
from repository.review_repository import ReviewRepository
from schemas.review_schema import *

MOCK_REVIEW = Review(**{
    "id": 1,
    "content": "Great movie!",
    "title_id": 2,
    "user_id": 3
})

@pytest.fixture
def mock_db_query():
    query = MagicMock(spec=Query)
    return query

@pytest.fixture
def mock_db_session():
    session = MagicMock(spec=Session)
    return session

def test_get_reviews(mock_db_session, mock_db_query):
    skip = 0
    limit = 10
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.offset.return_value = mock_db_query
    mock_db_query.limit.return_value = mock_db_query
    mock_db_query.all.return_value = [MOCK_REVIEW]

    repository = ReviewRepository(mock_db_session)
    result = repository.get_reviews(skip, limit)

    assert result == [MOCK_REVIEW]
    mock_db_query.offset.assert_called_once_with(skip)
    mock_db_query.limit.assert_called_once_with(limit)

def test_get_reviews_count(mock_db_session, mock_db_query):
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.count.return_value = 5

    repository = ReviewRepository(mock_db_session)
    result = repository.get_reviews_count()

    assert result == 5
    mock_db_query.count.assert_called_once()

def test_get_reviews_by_title(mock_db_session, mock_db_query):
    title_id = 2
    skip = 0
    limit = 10
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.offset.return_value = mock_db_query
    mock_db_query.limit.return_value = mock_db_query
    mock_db_query.all.return_value = [MOCK_REVIEW]

    repository = ReviewRepository(mock_db_session)
    result = repository.get_reviews_by_title(title_id, skip, limit)

    assert result == [MOCK_REVIEW]
    mock_db_query.filter.assert_called_once()
    mock_db_query.offset.assert_called_once_with(skip)
    mock_db_query.limit.assert_called_once_with(limit)

def test_get_reviews_by_title_count(mock_db_session, mock_db_query):
    title_id = 2
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.count.return_value = 3

    repository = ReviewRepository(mock_db_session)
    result = repository.get_reviews_by_title_count(title_id)

    assert result == 3
    mock_db_query.filter.assert_called_once()
    mock_db_query.count.assert_called_once()

def test_get_review_by_id(mock_db_session, mock_db_query):
    review_id = 1
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.first.return_value = MOCK_REVIEW

    repository = ReviewRepository(mock_db_session)
    result = repository.get_review_by_id(review_id)

    assert result == MOCK_REVIEW
    mock_db_query.filter.assert_called_once()
    mock_db_query.first.assert_called_once()

def test_create_review(mock_db_session, mock_db_query):
    review_data = ReviewCreate(**{
        "content": "Great movie!",
        "title_id": 2
    })
    user_id = 3
    created_review = Review(**{
        "id": 1,
        "content": review_data.content,
        "title_id": review_data.title_id,
        "user_id": user_id
    })
    mock_db_session.add.return_value = mock_db_query
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = created_review

    repository = ReviewRepository(mock_db_session)
    result = repository.create_review(review_data, user_id)

    assert result.content == review_data.content
    assert result.title_id == review_data.title_id
    assert result.user_id == user_id
    mock_db_session.add.assert_called_once_with(result)
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(result)

def test_delete_review(mock_db_session, mock_db_query):
    review_id = 1
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.first.return_value = MOCK_REVIEW
    mock_db_session.delete.return_value = None
    mock_db_session.commit.return_value = None

    repository = ReviewRepository(mock_db_session)
    result = repository.delete_review(review_id)

    assert result is True
    mock_db_query.filter.assert_called_once()
    mock_db_session.delete.assert_called_once_with(MOCK_REVIEW)
    mock_db_session.commit.assert_called_once()

def test_delete_review_not_found(mock_db_session, mock_db_query):
    review_id = 999
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.first.return_value = None

    repository = ReviewRepository(mock_db_session)
    result = repository.delete_review(review_id)
    
    assert result is False
    mock_db_query.filter.assert_called_once()
    mock_db_session.commit.assert_not_called()
