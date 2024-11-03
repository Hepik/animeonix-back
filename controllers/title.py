from fastapi import Depends, HTTPException, Query, APIRouter
from typing import Annotated
from schemas.title_schema import *
from service.title_service import TitleService


router = APIRouter(
    prefix="/titles"
)


@router.get("", response_model=TitleResponse)
def get_titles(service: Annotated[TitleService, Depends()], page: int = Query(1), limit: int = Query(10)):
    return service.get_titles(page=page, limit=limit)
    

@router.get("/{slug}", response_model=Title)
def get_title_by_slug(slug: str, service: Annotated[TitleService, Depends()]):
    title = service.get_title_by_slug(slug=slug)
    if not title:
        raise HTTPException(status_code=404, detail="Title not found")
    return title


@router.post("", response_model=Title)
def create_title(title: TitleCreate, service: Annotated[TitleService, Depends()]):
    return service.create_title(title=title)


@router.put("/{id}", response_model=Title)
def update_title(id: int, title: TitleCreate, service: Annotated[TitleService, Depends()]):
    return service.update_title(id=id, title=title)


@router.patch("/{id}", response_model=Title)
def partial_update_title(id: int, title: TitleUpdate, service: Annotated[TitleService, Depends()]):
    return service.partial_update_title(id=id, title=title)


@router.delete("/{id}", response_model=DeleteResponse)
def delete_title(id: int, service: Annotated[TitleService, Depends()]):
    service.delete_title(id=id)
    return {"detail": "Title deleted successfully"}
