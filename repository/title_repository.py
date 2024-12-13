import models.title
import schemas.title_schema
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from config.database import get_db


class TitleRepository:
    def __init__(self, session: Annotated[Session, Depends(get_db)]):
        self.db = session

    def get_titles(self, skip: int = 0, limit: int = 10):
        return self.db.query(models.title.Title).offset(skip).limit(limit).all()

    def get_title_by_id(self, id: int):
        return self.db.query(models.title.Title).filter(models.title.Title.id == id).first()

    def get_title_by_slug(self, slug: str):
        return self.db.query(models.title.Title).filter(models.title.Title.slug == slug).first()

    def get_title_count(self):
        return self.db.query(models.title.Title).count()
    
    def filter_titles_by_name(self, name: str, skip: int = 0, limit: int = 10):
        return (
            self.db.query(models.title.Title)
            .filter(models.title.Title.name.ilike(f"%{name}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_filtered_title_count(self, name: str) -> int:
        return (
            self.db.query(models.title.Title)
            .filter(models.title.Title.name.ilike(f"%{name}%"))
            .count()
        )

    def create_title(self, title: schemas.title_schema.TitleCreate):
        db_title = models.title.Title(
            name=title.name,
            description=title.description,
            trailer=title.trailer,
            image=title.image,
            slug=title.slug
        )
        self.db.add(db_title)
        self.db.commit()
        self.db.refresh(db_title)
        return db_title

    def partial_update_title(self, id: int, title_data: schemas.title_schema.TitleUpdate):
        db_title = self.db.query(models.title.Title).filter(models.title.Title.id == id).first()
        if not db_title:
            return None

        for field, value in title_data.dict(exclude_unset=True).items():
            setattr(db_title, field, value)

        self.db.commit()
        self.db.refresh(db_title)
        return db_title

    def delete_title(self, id: int):
        db_title = self.db.query(models.title.Title).filter(models.title.Title.id == id).first()
        if db_title:
            self.db.delete(db_title)
            self.db.commit()
            return True
        return False
