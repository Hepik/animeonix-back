import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session, Query
from repository.title_repository import TitleRepository
from models.title import Title
from models.review import Review
from schemas.title_schema import *

MOCK_TITLE = Title(**{
    "id": 1,
    "name": "Test Title",
    "description": "Test Description",
    "trailer": "https://example.com/trailer",
    "reviews": 5,
    "image": "/static/images/test.jpg",
    "slug": "test-title"
})

@pytest.fixture
def mock_db_query():
    query = MagicMock(spec=Query)
    return query

@pytest.fixture
def mock_db_session():
    session = MagicMock(spec=Session)
    return session

def test_get_titles(mock_db_session, mock_db_query):
    skip = 0
    limit = 10
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.outerjoin.return_value = mock_db_query
    mock_db_query.group_by.return_value = mock_db_query
    mock_db_query.offset.return_value = mock_db_query
    mock_db_query.limit.return_value = mock_db_query
    mock_db_query.all.return_value = [(MOCK_TITLE, 5)]
    
    repository = TitleRepository(mock_db_session)
    result = repository.get_titles(skip, limit)

    assert result != None
    assert len(result) == 1
    assert result[0].reviews == 5
    mock_db_query.offset.assert_called_once_with(skip)
    mock_db_query.limit.assert_called_once_with(limit)

def test_get_title_by_id(mock_db_session, mock_db_query):
    title_id = 1
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.first.return_value = MOCK_TITLE
    
    repository = TitleRepository(mock_db_session)
    result = repository.get_title_by_id(title_id)

    assert result == MOCK_TITLE
    mock_db_query.filter.assert_called_once()

def test_get_title_by_slug(mock_db_session, mock_db_query):
    slug = "test-title"
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.first.return_value = MOCK_TITLE
    
    repository = TitleRepository(mock_db_session)
    result = repository.get_title_by_slug(slug)

    assert result == MOCK_TITLE
    mock_db_query.filter.assert_called_once()

def test_get_title_count(mock_db_session, mock_db_query):
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.count.return_value = 5
    
    repository = TitleRepository(mock_db_session)
    result = repository.get_title_count()

    assert result == 5
    mock_db_query.count.assert_called_once()

def test_filter_titles_by_name(mock_db_session, mock_db_query):
    name = "Test"
    skip = 0
    limit = 10
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.offset.return_value = mock_db_query
    mock_db_query.limit.return_value = mock_db_query
    mock_db_query.all.return_value = [MOCK_TITLE]
    
    repository = TitleRepository(mock_db_session)
    result = repository.filter_titles_by_name(name, skip, limit)

    assert result == [MOCK_TITLE]
    mock_db_query.filter.assert_called_once()
    mock_db_query.offset.assert_called_once_with(skip)
    mock_db_query.limit.assert_called_once_with(limit)

def test_get_filtered_title_count(mock_db_session, mock_db_query):
    name = "Test"
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.count.return_value = 5
    
    repository = TitleRepository(mock_db_session)
    result = repository.get_filtered_title_count(name)

    assert result == 5
    mock_db_query.filter.assert_called_once()
    mock_db_query.count.assert_called_once()

def test_create_title(mock_db_session, mock_db_query):
    title_data = TitleCreate(**{
        "name": "New Title",
        "description": "New Description",
        "trailer": "https://example.com/trailer",
        "image": "/static/images/new.jpg",
        "slug": "new-title"
    })
    created_title = Title(**{
        "id": 1,
        "name": "New Title",
        "description": "New Description",
        "trailer": "https://example.com/trailer",
        "reviews": 0,
        "image": "/static/images/new.jpg",
        "slug": "new-title"
    })
    mock_db_session.query.return_value = mock_db_query
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = created_title

    repository = TitleRepository(mock_db_session)
    result = repository.create_title(title_data)

    assert result.name == title_data.name
    assert result.description == title_data.description
    assert result.trailer == title_data.trailer
    assert result.slug == title_data.slug
    assert result.image == title_data.image
    mock_db_session.add.assert_called_once_with(result)
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(result)

def test_partial_update_title(mock_db_session, mock_db_query):
    title_id = 1
    title_data = TitleUpdate(name="Updated Title")
    updated_title = Title(
        id=1,
        name="Updated Title",
        description="Test Description",
        trailer="https://example.com/trailer",
        reviews=5,
        image="/static/images/test.jpg",
        slug="test-title"
    )
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.first.return_value = MOCK_TITLE
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = updated_title

    repository = TitleRepository(mock_db_session)
    result = repository.partial_update_title(title_id, title_data)

    assert result is not None
    assert result.name == title_data.name
    assert result.id == title_id
    mock_db_query.filter.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(updated_title)

def test_delete_title(mock_db_session, mock_db_query):
    title_id = 1
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.first.return_value = MOCK_TITLE
    mock_db_session.delete.return_value = None
    mock_db_session.commit.return_value = None

    repository = TitleRepository(mock_db_session)
    result = repository.delete_title(title_id)

    assert result is True
    mock_db_query.filter.assert_called_once()
    mock_db_session.delete.assert_called_once_with(MOCK_TITLE)
    mock_db_session.commit.assert_called_once()

def test_delete_title_not_found(mock_db_session, mock_db_query):
    title_id = 999
    mock_db_session.query.return_value = mock_db_query
    mock_db_query.filter.return_value = mock_db_query
    mock_db_query.first.return_value = None

    repository = TitleRepository(mock_db_session)
    result = repository.delete_title(title_id)

    assert result is False
    mock_db_query.filter.assert_called_once()
    mock_db_session.commit.assert_not_called()
