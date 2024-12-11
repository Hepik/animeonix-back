from fastapi import HTTPException, Depends
from typing import Annotated
from schemas.title_schema import *
from repository.title_repository import TitleRepository


class TitleService:
    def __init__(self, repository: Annotated[TitleRepository, Depends()]):
        self.repository = repository

    def get_titles(self, page: int, limit: int, name: str):
        skip = (page - 1) * limit
        if name:
            titles = self.repository.filter_titles_by_name(name=name, skip=skip, limit=limit)
            total = self.repository.get_filtered_title_count(name=name)
        else:
            titles = self.repository.get_titles(skip=skip, limit=limit)
            total = self.repository.get_title_count()
        return {
            "titles": titles,
            "total": total,
            "page": page,
            "limit": limit
        }
    
    def get_title_by_slug(self, slug: str):
        title = self.repository.get_title_by_slug(slug=slug)
        if not title:
            raise HTTPException(status_code=404, detail="Title not found")
        return title


    def create_title(self, title: TitleCreate):
        db_title = self.repository.create_title(title=title)
        return db_title


    def update_title(self, id: int, title: TitleCreate):
        db_title = self.repository.update_title(id=id, title_data=title)
        if db_title is None:
            raise HTTPException(status_code=404, detail="Title not found")
        return db_title


    def partial_update_title(self, id: int, title: TitleUpdate):
        db_title = self.repository.partial_update_title(id=id, title_data=title)
        if db_title is None:
            raise HTTPException(status_code=404, detail="Title not found")
        return db_title


    def delete_title(self, id: int):
        title_deleted = self.repository.delete_title(id=id)
        if not title_deleted:
            raise HTTPException(status_code=404, detail="Title not found")
        return {"detail": "Title deleted successfully"}
