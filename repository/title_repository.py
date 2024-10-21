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
        titles = self.db.query(models.title.Title).offset(skip).limit(limit).all()
        
        for title in titles:
            title.image = f"http://localhost:8000/images/{title.image.split('/')[-1]}"

        return titles

    def get_title_by_id(self, id: int):
        title = self.db.query(models.title.Title).filter(models.title.Title.id == id).first()
        title.image = f"http://localhost:8000/images/{title.image.split('/')[-1]}"
        return title

    def get_title_by_slug(self, slug: str):
        title = self.db.query(models.title.Title).filter(models.title.Title.slug == slug).first()
        title.image = f"http://localhost:8000/images/{title.image.split('/')[-1]}"
        return title

    def get_title_count(self):
        return self.db.query(models.title.Title).count()

    def create_title(self, title: schemas.title_schema.TitleCreate):
        db_title = models.title.Title(
            name=title.name,
            description=title.description,
            trailer=title.trailer,
            likes=title.likes,
            dislikes=title.dislikes,
            reviews=title.reviews,
            image=title.image.split('/')[-1],
            slug=title.slug
        )
        self.db.add(db_title)
        self.db.commit()
        self.db.refresh(db_title)
        return db_title

    def update_title(self, title_id: int, title_data: schemas.title_schema.TitleCreate):
        db_title = self.db.query(models.title.Title).filter(models.title.Title.id == title_id).first()
        if not db_title:
            return None
        
        db_title.name = title_data.name
        db_title.description = title_data.description
        db_title.trailer = title_data.trailer
        db_title.likes = title_data.likes
        db_title.dislikes = title_data.dislikes
        db_title.reviews = title_data.reviews
        db_title.image = title_data.image.split('/')[-1]
        db_title.slug = title_data.slug

        self.db.commit()
        self.db.refresh(db_title)
        return db_title


    def partial_update_title(self, title_id: int, title_data: schemas.title_schema.TitleUpdate):
        db_title = self.db.query(models.title.Title).filter(models.title.Title.id == title_id).first()
        if not db_title:
            return None

        for field, value in title_data.dict(exclude_unset=True).items():
            setattr(db_title, field, value)

        self.db.commit()
        self.db.refresh(db_title)
        return db_title

    def delete_title(self, title_id: int):
        db_title = self.db.query(models.title.Title).filter(models.title.Title.id == title_id).first()
        if db_title:
            self.db.delete(db_title)
            self.db.commit()
            return True
        return False
