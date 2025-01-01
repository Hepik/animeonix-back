import pytest
from unittest.mock import MagicMock
from models.title import Title
from schemas.title_schema import *
from service.title_service import TitleService
from repository.title_repository import TitleRepository
from fastapi import HTTPException, status


MOCK_TITLES = [
    Title(**{
        "id": 1,
        "name": "Test Title 1",
        "description": "Description of test title 1",
        "trailer": "example_trailer_1",
        "reviews": 10,
        "image": "/static/titles/test1.jpg",
        "slug": "test-title-1",
    }),
    Title(**{
        "id": 2,
        "name": "Test Title 2",
        "description": "Description of test title 2",
        "trailer": "example_trailer_2",
        "reviews": 5,
        "image": "/static/titles/test2.jpg",
        "slug": "test-title-2",
    }),
]

MOCK_FILTERED_TITLES = [
    Title(**{
        "id": 3,
        "name": "Filtered Title 1",
        "description": "Filtered description 1",
        "trailer": "example_trailer_filtered_1",
        "reviews": 2,
        "image": "/static/titles/filtered1.jpg",
        "slug": "filtered-title-1",
    }),
]

MOCK_TOTAL_COUNT = 10
MOCK_FILTERED_COUNT = 1

@pytest.fixture
def mock_title_repository():
    repo = MagicMock(spec=TitleRepository)
    return repo

@pytest.fixture
def title_service(mock_title_repository):
    return TitleService(mock_title_repository)


def test_get_titles(title_service, mock_title_repository):
    mock_title_repository.get_titles.return_value = MOCK_TITLES
    mock_title_repository.get_title_count.return_value = MOCK_TOTAL_COUNT

    result = title_service.get_titles(page=1, limit=10, name="")

    assert result["titles"] == MOCK_TITLES
    assert result["total"] == MOCK_TOTAL_COUNT
    assert result["page"] == 1
    assert result["limit"] == 10
    mock_title_repository.get_titles.assert_called_once_with(skip=0, limit=10)
    mock_title_repository.get_title_count.assert_called_once()


def test_filter_titles_by_name(title_service, mock_title_repository):
    mock_title_repository.filter_titles_by_name.return_value = MOCK_FILTERED_TITLES
    mock_title_repository.get_filtered_title_count.return_value = MOCK_FILTERED_COUNT

    result = title_service.get_titles(page=1, limit=10, name="Filtered")

    assert result["titles"] == MOCK_FILTERED_TITLES
    assert result["total"] == MOCK_FILTERED_COUNT
    mock_title_repository.filter_titles_by_name.assert_called_once_with(name="Filtered", skip=0, limit=10)
    mock_title_repository.get_filtered_title_count.assert_called_once()


def test_filter_titles_no_results(title_service, mock_title_repository):
    mock_title_repository.filter_titles_by_name.return_value = []
    mock_title_repository.get_filtered_title_count.return_value = 0

    result = title_service.get_titles(page=1, limit=10, name="NonExisting")

    assert result["titles"] == []
    assert result["total"] == 0
    mock_title_repository.filter_titles_by_name.assert_called_once_with(name="NonExisting", skip=0, limit=10)
    mock_title_repository.get_filtered_title_count.assert_called_once()


def test_combined_get_titles_and_filter(title_service, mock_title_repository):
    mock_title_repository.get_titles.return_value = MOCK_TITLES
    mock_title_repository.get_title_count.return_value = MOCK_TOTAL_COUNT

    result = title_service.get_titles(page=2, limit=10, name="")

    assert result["titles"] == MOCK_TITLES
    assert result["total"] == MOCK_TOTAL_COUNT
    assert result["page"] == 2
    assert result["limit"] == 10
    mock_title_repository.get_titles.assert_called_once_with(skip=10, limit=10)
    mock_title_repository.get_title_count.assert_called_once()


def test_combined_get_titles_with_name_filter(title_service, mock_title_repository):
    mock_title_repository.filter_titles_by_name.return_value = MOCK_FILTERED_TITLES
    mock_title_repository.get_filtered_title_count.return_value = MOCK_FILTERED_COUNT

    result = title_service.get_titles(page=1, limit=10, name="Filtered")

    assert result["titles"] == MOCK_FILTERED_TITLES
    assert result["total"] == MOCK_FILTERED_COUNT
    mock_title_repository.filter_titles_by_name.assert_called_once_with(name="Filtered", skip=0, limit=10)
    mock_title_repository.get_filtered_title_count.assert_called_once()


def test_get_title_by_slug_found(title_service, mock_title_repository):
    mock_title_repository.get_title_by_slug.return_value = MOCK_TITLES[0]

    result = title_service.get_title_by_slug(slug="test-title-1")

    assert result == MOCK_TITLES[0]
    mock_title_repository.get_title_by_slug.assert_called_once_with(slug="test-title-1")


def test_get_title_by_slug_not_found(title_service, mock_title_repository):
    mock_title_repository.get_title_by_slug.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        title_service.get_title_by_slug(slug="non-existing-title")
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Title not found"
    mock_title_repository.get_title_by_slug.assert_called_once_with(slug="non-existing-title")


def test_create_title(title_service, mock_title_repository):
    new_title_data = {
        "name": "New Test Title",
        "description": "Test description",
        "trailer": "example_trailer",
        "reviews": 0,
        "image": "/static/titles/new_test_title.jpg",
        "slug": "new-test-title",
    }
    
    created_title_data = {
        "id": 1,
        **new_title_data
    }
    
    mock_title_repository.create_title.return_value = Title(**created_title_data)
    
    created_title = title_service.create_title(new_title_data)
    
    assert created_title.id == 1
    assert created_title.name == "New Test Title"
    assert created_title.description == "Test description"
    assert created_title.reviews == 0
    assert created_title.slug == "new-test-title"
    mock_title_repository.create_title.assert_called_once_with(new_title_data)


def test_partial_update_title_success(title_service, mock_title_repository):
    updated_data = TitleUpdate(**{
        "name": "Updated Title",
        "description": "Updated description",
        "trailer": None,
        "reviews": None,
        "image": None,
        "slug": None
    })
    updated_title_data = Title(**{
        "id": 1,
        "name": "Updated Title",
        "description": "Updated description",
        "trailer": "example_trailer_1",
        "reviews": 10,
        "image": "/static/titles/test1.jpg",
        "slug": "test-title-1",
    })

    mock_title_repository.partial_update_title.return_value = updated_title_data

    updated_title = title_service.partial_update_title(id=1, title=updated_data)

    assert updated_title.id == 1
    assert updated_title.name == "Updated Title"
    assert updated_title.description == "Updated description"
    mock_title_repository.partial_update_title.assert_called_once_with(id=1, title_data=updated_data)


def test_partial_update_title_not_found(title_service, mock_title_repository):
    updated_data = Title(**{
        "id": 1,
        "name": "Non-existing Title",
        "description": "Non-existing description",
        "trailer": "example_trailer_1",
        "reviews": 10,
        "image": "/static/titles/test1.jpg",
        "slug": "test-title-1",
    })

    mock_title_repository.partial_update_title.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        title_service.partial_update_title(id=999, title=updated_data)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Title not found"
    mock_title_repository.partial_update_title.assert_called_once_with(id=999, title_data=updated_data)


def test_delete_title_success(title_service, mock_title_repository):
    mock_title_repository.delete_title.return_value = True

    result = title_service.delete_title(id=1)

    assert result == {"detail": "Title deleted successfully"}
    mock_title_repository.delete_title.assert_called_once_with(id=1)


def test_delete_title_not_found(title_service, mock_title_repository):
    mock_title_repository.delete_title.return_value = False

    with pytest.raises(HTTPException) as exc_info:
        title_service.delete_title(id=999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Title not found"
    mock_title_repository.delete_title.assert_called_once_with(id=999)
